/*
 *  dpcsh_libfunq.c
 *
 *  Created by Shweta on 2018-02-12.
 *  Copyright © 2016 Fungible. All rights reserved.
 */

#include <stdio.h>
#include <unistd.h>
#include "dpcsh_libfunq.h"
#include "dpcsh_log.h"

// libfunq is supported only for Linux
#ifdef WITH_LIBFUNQ
#include "libfunq.h"

#define DMA_BUFSIZE_BYTES 	(16384)
#define ASQE_SIZE			(128)
#define ACQE_SIZE			(128)
#define ASQ_DEPTH			(DMA_BUFSIZE_BYTES / ASQE_SIZE)
#define ACQ_DEPTH			(DMA_BUFSIZE_BYTES / ACQE_SIZE)
#define FIRST_LEVEL_SGL_N			(5)
#define MAX_BUFFERS_PER_OPERATION (FUNQ_MAX_DMA_BUFFERS / 4)
#define FUNQ_SYNC_CMD_TIMEOUT_MS	(0) // no timeout
#define FUNQ_CONNECT_CMD_TIMEOUT_MS	(1000 * 60)

static_assert((FUNQ_MAX_CONNECTIONS*2 <= ASQ_DEPTH) && (FUNQ_MAX_CONNECTIONS*2 <= ACQ_DEPTH),
	"Queue must be deep enough to support all the context");
static_assert(FUNQ_MAX_DMA_BUFFERS >= FUNQ_MAX_CONNECTIONS*2,
	"Must be at least 2 buffers per each connection");

#define CEILING(x,y) (((x) + (y) - 1) / (y))
#define SECOND_LEVEL_SGL_N (CEILING(FUNQ_MAX_DATA_BYTES, DMA_BUFSIZE_BYTES))

struct dpc_pending_allocation {
	int rx_index, tx_index;
	pthread_cond_t ready;
	struct dpc_pending_allocation *next;
};

struct dpc_funq_buffer {
	void *dma_addr_local;
	dma_addr_t dma_addr_dpu;
	bool used;
};

struct dpc_funq_handle {
	funq_handle_t handle;

	struct dpc_funq_buffer buffers[FUNQ_MAX_DMA_BUFFERS];

	int free_buffers_n;
	struct dpc_pending_allocation *pending;

	size_t connections_active;
	pthread_mutex_t lock;
	bool debug;
};

struct dpc_funq_connection {
	struct dpc_funq_handle *dpc_handle;

	uint16_t id;

	int send_buffer_idx;
	int recv_buffer_idx;

	bool receiver_alive;
	bool receiver_closing_connection;
	pthread_mutex_t receive_lock;
	pthread_cond_t receiver_closed;

	dpc_funq_callback_t callback;
	void *callback_context;
};

struct dpc_funq_context {
	struct dpc_funq_connection *connection;
	struct fun_admin_dpc_req *request;

	int sgl_first_n;
	int sgl_second_n;

	int *sgl_idx;
	int sgl_n;

	struct fun_ptr_and_size response;
	size_t response_offset;
};

static int dpc_allocate_buffer(struct dpc_funq_handle *h)
{
	if (!h->free_buffers_n) return -1;
	for (int i = 0; i < FUNQ_MAX_DMA_BUFFERS; i++) {
		if (h->buffers[i].used) continue;
		h->buffers[i].used = true;
		h->free_buffers_n--;
		return i;
	}
	return -1;
}

static void dpc_free_buffer(struct dpc_funq_handle *h, int idx)
{
	if (idx < 0) return;

	h->buffers[idx].used = false;

	struct dpc_pending_allocation *p = h->pending;

	if (!p) {
		h->free_buffers_n++;
		return;
	}

	if (p->tx_index == -1) {
		p->tx_index = idx;
		return;
	}

	if (p->rx_index == -1) {
		p->rx_index = idx;
	} else {
		log_error("allocation inconsistency\n");
	}

	pthread_cond_signal(&p->ready);
	h->pending = p->next;
	free(p);
}

static void dpc_allocate_rx_tx(struct dpc_funq_connection *connection)
{
	connection->send_buffer_idx = dpc_allocate_buffer(connection->dpc_handle);
	connection->recv_buffer_idx = dpc_allocate_buffer(connection->dpc_handle);
}

static void dpc_deallocate_rx_tx(struct dpc_funq_connection *connection)
{
	dpc_free_buffer(connection->dpc_handle, connection->send_buffer_idx);
	dpc_free_buffer(connection->dpc_handle, connection->recv_buffer_idx);
}

static void dpc_add_pending(struct dpc_funq_handle *h, struct dpc_pending_allocation *p)
{
	struct dpc_pending_allocation **last;
	last = &h->pending;
	while (*last != NULL) {
		*last = (*last)->next;
	}
	*last = p;
}

struct dpc_funq_connection *dpc_funq_open_connection(struct dpc_funq_handle *dpc_handle)
{
	struct fun_admin_dpc_req c = {};
	struct fun_admin_dpc_rsp r = {};

	struct dpc_funq_connection *connection = (struct dpc_funq_connection *)calloc(1, sizeof(struct dpc_funq_connection));
	connection->dpc_handle = dpc_handle;

	if (pthread_cond_init(&connection->receiver_closed, NULL) != 0 ||
		  pthread_mutex_init(&connection->receive_lock, NULL) != 0) {
		log_error("pthread cond and lock error");
		free(connection);
		return NULL;
	}

	fun_admin_req_common_init(&c.common, FUN_ADMIN_OP_DPC,
			sizeof (c) >> 3, 0 /* flags */, 0 /* suboff8 */, 0 /* cid */);
	fun_admin_dpc_open_connection_req_init(&c, FUN_ADMIN_DPC_SUBOP_OPEN_CONNECTION, 0, 0);

	int ret = funq_admin_submit_sync_cmd(dpc_handle->handle,
			&c.common, &r.common, sizeof(r), FUNQ_SYNC_CMD_TIMEOUT_MS);

	if (ret != 0 || r.u.open.code != FUN_ADMIN_DPC_ISSUE_CMD_RESP_COMPLETE) {
		log_error("failed to open the connection, ret = %d, code = %" PRId8 "\n", ret, r.u.open.code);
		free(connection);
		return NULL;
	}

	connection->id = r.u.open.connection_id;

	log_debug(dpc_handle->debug, "dpc_open_connection successful, id=%" PRIu16 "\n", connection->id);

	pthread_mutex_lock(&dpc_handle->lock);
	dpc_handle->connections_active++;

	dpc_allocate_rx_tx(connection);
	if (connection->recv_buffer_idx == -1 || connection->send_buffer_idx == -1) {
		struct dpc_pending_allocation *a = calloc(1, sizeof(struct dpc_pending_allocation));
		a->rx_index = connection->recv_buffer_idx;
		a->tx_index = connection->send_buffer_idx;
		a->next = NULL;

		log_debug(dpc_handle->debug, "waiting for buffers to be available\n");

		if (pthread_cond_init(&a->ready, NULL) != 0) {
			log_error("pthread_cond_init() error");
			free(a);
			goto fail;
		}

		dpc_add_pending(dpc_handle, a);

		ret = pthread_cond_wait(&a->ready, &dpc_handle->lock);
		if (ret) {
			log_error("failed to wait for release of buffers, code = %d\n", ret);
		}

		connection->recv_buffer_idx = a->rx_index;
		connection->send_buffer_idx = a->tx_index;
		if (a->rx_index == -1 || a->tx_index == -1) {
			log_error("failed to allocate after waiting\n");
			ret = 1;
		}
	}

	log_debug(dpc_handle->debug, "rx and tx buffers allocated\n");

	if (ret) goto fail;

	pthread_mutex_unlock(&dpc_handle->lock);

	return connection;

fail:
	dpc_deallocate_rx_tx(connection);
	dpc_handle->connections_active--;
	pthread_mutex_unlock(&dpc_handle->lock);
	free(connection);
	return NULL;
}

extern bool dpc_funq_close_connection(struct dpc_funq_connection *connection)
{
	struct fun_admin_dpc_req c = {};
	struct fun_admin_dpc_rsp r = {};

	connection->receiver_closing_connection = true;

	fun_admin_req_common_init(&c.common, FUN_ADMIN_OP_DPC,
			sizeof (c) >> 3, 0 /* flags */, 0 /* suboff8 */, 0 /* cid */);
	fun_admin_dpc_close_connection_req_init(&c, FUN_ADMIN_DPC_SUBOP_CLOSE_CONNECTION,
			0, 0, cpu_to_dpu16(connection->id));

	funq_handle_t handle = connection->dpc_handle->handle;
	int ret = funq_admin_submit_sync_cmd(handle,
			&c.common, &r.common, sizeof(r), FUNQ_SYNC_CMD_TIMEOUT_MS);

	if (ret != 0) {
		log_error("failed to close the connection, code = %d\n", ret);
		return false;
	}

	pthread_mutex_lock(&connection->receive_lock);
	if (connection->receiver_alive) {
		ret = pthread_cond_wait(&connection->receiver_closed, &connection->receive_lock);
		if (ret) {
			log_error("failed to wait for receiver to stop, code = %d\n", ret);
		}
	}
	connection->receiver_closing_connection = false;
	pthread_mutex_unlock(&connection->receive_lock);

	log_debug(connection->dpc_handle->debug, "dpc_close_connection successful\n");

	pthread_mutex_lock(&connection->dpc_handle->lock);
	dpc_deallocate_rx_tx(connection);
	connection->dpc_handle->connections_active--;
	pthread_mutex_unlock(&connection->dpc_handle->lock);
	free(connection);
	return true;
}

static int dpc_create_cmd(funq_handle_t handle)
{
	struct fun_admin_dpc_req c = {};
	struct fun_admin_dpc_rsp r = {};

	fun_admin_req_common_init(&c.common, FUN_ADMIN_OP_DPC,
			sizeof (c) >> 3, 0 /* flags */, 0 /* suboff8 */, 0 /* cid */);
	fun_admin_dpc_create_req_init(&c, FUN_ADMIN_SUBOP_CREATE,
			FUN_ADMIN_RES_CREATE_FLAG_ALLOCATOR /* flag */, 0 /* id */);

	return funq_admin_submit_sync_cmd(handle,
			&c.common, &r.common, sizeof(r), FUNQ_CONNECT_CMD_TIMEOUT_MS);
}

static size_t fun_admin_request_size(size_t first_level_sgl_n)
{
	size_t total_sgl_len = sizeof(struct fun_subop_sgl) * first_level_sgl_n;
	return sizeof(struct fun_admin_dpc_req) + total_sgl_len;
}

static void fill_sgl_request_header(struct dpc_funq_context *context, bool send)
{
	struct fun_subop_sgl *sgl = context->request->sgl;
	struct dpc_funq_handle *dpc_handle = context->connection->dpc_handle;
	struct dpc_funq_buffer *buffers = dpc_handle->buffers;
	bool direct = context->sgl_second_n == 0;

	fun_admin_req_common_init(&context->request->common,
			FUN_ADMIN_OP_DPC, fun_admin_request_size(context->sgl_first_n) >> 3,
			0 /* flags */, 0 /* suboff8 */, 0 /* cid */);

	for (size_t i = 0; i < context->sgl_first_n; i++) {
		fun_subop_sgl_init(sgl + i,
			direct ? (send ? FUN_DATAOP_GL : FUN_DATAOP_SL) : FUN_DATAOP_INDIRECT,
			0 /* flags */, 1 /* nsgl */, DMA_BUFSIZE_BYTES /* sgl_len */,
			cpu_to_dpu64((uint64_t)buffers[context->sgl_idx[i]].dma_addr_dpu) /* sgl_data */);
	}

	for (size_t i = 0; i < context->sgl_second_n; i++) {
		size_t first_level_index = i * sizeof(struct fun_subop_sgl) / DMA_BUFSIZE_BYTES;
		size_t first_level_offset = i - first_level_index * (DMA_BUFSIZE_BYTES / sizeof(struct fun_subop_sgl));
		struct fun_subop_sgl *buffer = buffers[context->sgl_idx[first_level_index]].dma_addr_local;
		fun_subop_sgl_init(buffer + first_level_offset, (send ? FUN_DATAOP_GL : FUN_DATAOP_SL), 0, 1,
			DMA_BUFSIZE_BYTES, cpu_to_dpu64((uint64_t)buffers[context->sgl_idx[context->sgl_first_n + i]].dma_addr_dpu));
	}
}

static void fill_send_request_header(struct dpc_funq_context *context,
	size_t full_size, size_t offset, size_t size)
{
	struct dpc_funq_handle *dpc_handle = context->connection->dpc_handle;

	fill_sgl_request_header(context, true);

	log_debug(dpc_handle->debug, "preparing send request connection_id=%" PRIu16 ", size=%zu, offset=%zu, full_size=%zu\n", context->connection->id, size, offset, full_size);
	log_debug(dpc_handle->debug, "sgl_n=%d, sgl_first_n=%d, sgl_second_n=%d\n", context->sgl_n, context->sgl_first_n, context->sgl_second_n);

	fun_admin_dpc_send_data_req_init(context->request,
			FUN_ADMIN_DPC_SUBOP_SEND_DATA, 0, 0,
			cpu_to_dpu16(context->connection->id),
			cpu_to_dpu32(full_size), cpu_to_dpu32(offset), cpu_to_dpu32(size));
}

static void fill_recv_request_header(struct dpc_funq_context *context)
{
	struct dpc_funq_handle *dpc_handle = context->connection->dpc_handle;

	fill_sgl_request_header(context, false);

	size_t buffer_size = (context->sgl_second_n ? context->sgl_second_n : context->sgl_first_n) * DMA_BUFSIZE_BYTES;

	log_debug(dpc_handle->debug, "preparing receive request connection_id=%" PRIu16 ", size=%zu\n", context->connection->id, buffer_size);
	log_debug(dpc_handle->debug, "sgl_n=%d, sgl_first_n=%d, sgl_second_n=%d\n", context->sgl_n, context->sgl_first_n, context->sgl_second_n);

	fun_admin_dpc_receive_data_req_init(context->request,
		FUN_ADMIN_DPC_SUBOP_RECEIVE_DATA, 0, 0,
		cpu_to_dpu16(context->connection->id),
		cpu_to_dpu32(buffer_size));
}

static void fill_sgl_buffers(struct dpc_funq_buffer *buffers, int *sgl_idx, struct fun_ptr_and_size data)
{
	size_t output_buffers_n = CEILING(data.size, DMA_BUFSIZE_BYTES);
	for (size_t index = 0; index < output_buffers_n; index++) {
		memcpy(buffers[sgl_idx[index]].dma_addr_local, data.ptr + index * DMA_BUFSIZE_BYTES, min((size_t)DMA_BUFSIZE_BYTES, data.size - index * DMA_BUFSIZE_BYTES));
	}
}

static void dpc_split_sgl_layers(struct dpc_funq_context *context)
{
	bool direct = (context->sgl_n <= FIRST_LEVEL_SGL_N);
	context->sgl_first_n = context->sgl_n;
	context->sgl_second_n = 0;
	if (!direct) {
		context->sgl_first_n = CEILING(context->sgl_n * sizeof(struct fun_subop_sgl), DMA_BUFSIZE_BYTES);
		context->sgl_first_n = min(context->sgl_first_n, FIRST_LEVEL_SGL_N);
		context->sgl_second_n = context->sgl_n - context->sgl_first_n;
		context->sgl_second_n = min(context->sgl_second_n, context->sgl_first_n * DMA_BUFSIZE_BYTES / ((int)sizeof(struct fun_subop_sgl)));
	}
}

static bool dpc_send_data_cmd(size_t *position, struct dpc_funq_connection *connection,
	struct fun_ptr_and_size data, int *allocations, int allocations_n)
{
	struct fun_admin_dpc_rsp response = {};
	struct dpc_funq_context context = {};
	bool direct = (allocations_n <= FIRST_LEVEL_SGL_N);
	int data_buffers_n = allocations_n;

	context.sgl_n = allocations_n;
	dpc_split_sgl_layers(&context);

	if (!direct) {
		data_buffers_n = context.sgl_second_n;
	}

	context.sgl_idx = allocations;
	context.connection = connection;
	context.request = calloc(1, fun_admin_request_size(context.sgl_first_n));

	struct fun_ptr_and_size chunk = {.ptr = data.ptr + *position,
		.size = min(data.size - *position, (size_t)data_buffers_n * DMA_BUFSIZE_BYTES)};

	fill_send_request_header(&context, data.size, *position, chunk.size);

	struct dpc_funq_buffer *buffers = &(connection->dpc_handle->buffers[0]);
	int *sgl_idx = context.sgl_idx;
	if (!direct) sgl_idx += context.sgl_first_n;

	fill_sgl_buffers(buffers, sgl_idx, chunk);

	int rc = funq_admin_submit_sync_cmd(connection->dpc_handle->handle,
			&context.request->common, &response.common, sizeof(response), FUNQ_SYNC_CMD_TIMEOUT_MS);

	free(context.request);

	if (rc) {
		log_error("send failed, code %d\n", rc);
		return false;
	}

	bool last_buffer = (data.size <= *position + chunk.size);
	if ((response.u.cmd.code == FUN_ADMIN_DPC_ISSUE_CMD_RESP_COMPLETE && last_buffer)
		|| (response.u.cmd.code == FUN_ADMIN_DPC_ISSUE_CMD_RESP_PARTIAL && !last_buffer)) {
		*position += chunk.size;
		return true;
	}

	log_error("unexpected return code, code %d, last_buffer = %s\n", response.u.cmd.code, (last_buffer ? "true": "false"));
	return false;
}

static bool dpc_init_buffers(int **allocations, int *allocations_n,
	struct dpc_funq_handle *handle, int reserved_idx) {
	*allocations_n = 1;
	*allocations = malloc(sizeof(int *) * MAX_BUFFERS_PER_OPERATION);
	if (!*allocations) return false;
	**allocations = reserved_idx;
	return true;
}

static void dpc_reallocate_buffers(int **allocations, int *allocations_n,
	struct dpc_funq_handle *dpc_handle, int data_buffers_n)
{
	// most frequent case, no need to allocate or deallocate anything
	if (*allocations_n == 1 && data_buffers_n == 1) {
		return;
	}

	pthread_mutex_lock(&dpc_handle->lock);

	if (data_buffers_n > FIRST_LEVEL_SGL_N) {
		data_buffers_n += CEILING(sizeof(struct fun_subop_sgl) * data_buffers_n, DMA_BUFSIZE_BYTES);
	}

	while (dpc_handle->pending != NULL && *allocations_n > 1) { // first buffer is reserved
		dpc_free_buffer(dpc_handle, (*allocations)[--(*allocations_n)]);
	}

	int new_allocations_n = min(min(dpc_handle->free_buffers_n, data_buffers_n), MAX_BUFFERS_PER_OPERATION);

	for (int i = new_allocations_n; i < *allocations_n; i++) {
		dpc_free_buffer(dpc_handle, (*allocations)[i]);
	}

	for (int i = *allocations_n; i < new_allocations_n; i++) {
		(*allocations)[i] = dpc_allocate_buffer(dpc_handle);
	}

	*allocations_n = new_allocations_n;
	pthread_mutex_unlock(&dpc_handle->lock);
}

static void dpc_free_buffers(int *allocations, int allocations_n, struct dpc_funq_handle *dpc_handle)
{
	pthread_mutex_lock(&dpc_handle->lock);
	for (int i = 1; i < allocations_n; i++) { // first buffer is reserved
		dpc_free_buffer(dpc_handle, allocations[i]);
	}
	free(allocations);
	pthread_mutex_unlock(&dpc_handle->lock);
}

static bool dpc_recv_data_cmd(struct dpc_funq_context *context);

static void free_context(struct dpc_funq_context *context)
{
	dpc_free_buffers(context->sgl_idx, context->sgl_n, context->connection->dpc_handle);
	free(context->request);
	free(context->response.ptr);
	free(context);
}

static void dpc_funq_stop_receiver(struct dpc_funq_context *context)
{
	pthread_mutex_lock(&context->connection->receive_lock);

	if (context->connection->receiver_closing_connection) {
		pthread_cond_signal(&context->connection->receiver_closed);
	} else {
		log_error("stopping the receiver unexpectedly\n");
	}

	context->connection->receiver_alive = false;
	pthread_mutex_unlock(&context->connection->receive_lock);
}

static void dpc_proccess_recv_response(void *response, void *ctx)
{
	struct dpc_funq_context *context = ctx;
	struct fun_admin_dpc_rsp *r = response;
	log_debug(context->connection->dpc_handle->debug, "starting the receive\n");

	if (r->u.receive.code == FUN_ADMIN_DPC_ISSUE_CMD_RESP_FAIL) {
		dpc_funq_stop_receiver(context);
		free_context(context);
		return;
	}

	log_debug(context->connection->dpc_handle->debug, "rx size=%" PRIu32 ", offset=%" PRIu32 ", full_size=%" PRIu32 "\n",
		r->u.receive.resp_size, r->u.receive.resp_offset, r->u.receive.resp_full_size);

	if (!context->response.ptr) {
		context->response.ptr = malloc(r->u.receive.resp_full_size);
		context->response.size = r->u.receive.resp_full_size;
		if (!context->response.ptr) {
			log_error("oom when allocating space for the response\n");
			dpc_funq_stop_receiver(context);
			free_context(context);
			return;
		}
		context->response_offset = 0;
	}

	if (r->u.receive.resp_offset != context->response_offset) {
		log_error("unexpected offset when processing response %" PRIu32 " != %zu\n", r->u.receive.resp_offset, context->response_offset);
		dpc_funq_stop_receiver(context);
		free_context(context);
		return;
	}

	int *sgl_idx = (context->sgl_second_n == 0) ? context->sgl_idx : (context->sgl_idx + context->sgl_first_n);
	int sgl_n = (context->sgl_second_n == 0) ? context->sgl_first_n : context->sgl_second_n;
	size_t position = 0;

	for (int i = 0; i < sgl_n; i++) {
		int chunk_size = min(DMA_BUFSIZE_BYTES, (int)r->u.receive.resp_size - (int)position);
		if (chunk_size <= 0) break;
		memcpy(context->response.ptr + context->response_offset + position,
			context->connection->dpc_handle->buffers[sgl_idx[i]].dma_addr_local, chunk_size);
		position += chunk_size;
	}

	context->response_offset += r->u.receive.resp_size;

	int new_buffers_n = CEILING(context->response.size - context->response_offset, DMA_BUFSIZE_BYTES);

	if (r->u.receive.code == FUN_ADMIN_DPC_ISSUE_CMD_RESP_COMPLETE) {
		context->connection->callback(context->response, context->connection->callback_context);
		free(context->response.ptr);
		context->response.ptr = NULL;
		new_buffers_n = 1;
	}

	dpc_reallocate_buffers(&context->sgl_idx, &context->sgl_n, context->connection->dpc_handle, new_buffers_n);
	dpc_split_sgl_layers(context);

	if (!dpc_recv_data_cmd(context)) {
		dpc_funq_stop_receiver(context);
		free_context(context);
		return;
	}
}

static bool dpc_recv_data_cmd(struct dpc_funq_context *context)
{
	fill_recv_request_header(context);
	struct dpc_funq_handle *dpc_handle = context->connection->dpc_handle;

	int rv = funq_admin_submit_async_cmd(dpc_handle->handle,
			&context->request->common, dpc_proccess_recv_response, fun_admin_request_size(FIRST_LEVEL_SGL_N), context);
	
	if (rv != 0) {
		log_error("unexpected return code from funq_admin_submit_async_cmd = %d\n", rv);
		return false;
	}

	return true;
}

static bool dpc_first_recv_data_cmd(struct dpc_funq_connection *connection)
{
	struct dpc_funq_context *context = calloc(1, sizeof(struct dpc_funq_context));
	context->sgl_first_n = 1;
	context->connection = connection;
	context->request = calloc(1, fun_admin_request_size(FIRST_LEVEL_SGL_N));
	if (!dpc_init_buffers(&context->sgl_idx, &context->sgl_n,
		connection->dpc_handle, connection->recv_buffer_idx)) {
		log_error("failed to initialize buffers\n");
		free(context);
		return false;
	}

	return dpc_recv_data_cmd(context);
}

static int dpc_destroy_cmd(funq_handle_t handle)
{
	struct fun_admin_dpc_req c = {};
	struct fun_admin_dpc_rsp r = {};
	fun_admin_req_common_init(&c.common, FUN_ADMIN_OP_DPC,
			sizeof (c) >> 3, 0 /* flags */, 0 /* suboff8 */, 0 /* cid */);
	fun_admin_dpc_destroy_req_init(&c, FUN_ADMIN_SUBOP_DESTROY,
			0 /* flag */, 0 /* id */);

	return funq_admin_submit_sync_cmd(handle,
			&c.common, &r.common, sizeof(r), FUNQ_SYNC_CMD_TIMEOUT_MS);
}

static funq_handle_t dpc_admin_queue_init(const char *devname)
{
	/* Admin Q Req */
	struct fun_admin_queue_req aqreq = {
		.cqe_size_log2 = ilog2(ACQE_SIZE),
		.sqe_size_log2 = ilog2(ASQE_SIZE),
		.cq_depth      = ACQ_DEPTH,
		.sq_depth      = ASQ_DEPTH,
		.create_rq     = false,
		.use_irq       = false,
	};

	const char *devname_p = NULL;
	if (strcmp(devname, "auto") != 0) {
		devname_p = devname;
	}

	funq_handle_t handle;

	/* devname NULL = auto discover */
	int rc = funq_admin_init(DEVTYPE_VFIO, devname_p, &aqreq, &handle);

	if (rc) {
		log_error("funq_admin_init failed\n");
		exit(rc);
	}

	return handle;
}

struct dpc_funq_handle *dpc_funq_init(const char *devname, bool debug)
{
	struct dpc_funq_handle *handle = calloc(1, sizeof(struct dpc_funq_handle));

	if (handle == NULL) {
		log_error("oom when allocating dpc_funq_handle\n");
		return NULL;
	}

	handle->debug = debug;

	if (pthread_mutex_init(&handle->lock, NULL) != 0) {
		free(handle);
		log_error("failed to initialize pthread mutex\n");
		return NULL;
	}

	handle->handle = dpc_admin_queue_init(devname);

	log_debug(handle->debug, "admin_queue_init successful\n");

	if (dpc_create_cmd(handle->handle) != 0) {
		free(handle);
		log_error("failed to run create command\n");
		return NULL;
	}

	log_debug(handle->debug, "dpc_create_cmd successful\n");

	for (int i = 0; i < FUNQ_MAX_DMA_BUFFERS; i++) {
		handle->buffers[i].dma_addr_local = (uint8_t *)funq_dma_alloc(handle->handle, DMA_BUFSIZE_BYTES, &(handle->buffers[i].dma_addr_dpu));
		if (!handle->buffers[i].dma_addr_local) {
			log_error("failed to allocate dma buffers\n");
			dpc_funq_destroy(handle);
			return NULL;
		}
	}
	handle->free_buffers_n = FUNQ_MAX_DMA_BUFFERS;

	log_debug(handle->debug, "DMA buffers allocated\n");

	return handle;
}

bool dpc_funq_destroy(struct dpc_funq_handle *dpc_handle)
{
	pthread_mutex_lock(&dpc_handle->lock);

	if (dpc_handle->connections_active > 0) {
		log_error("can't close dpc_handle, need to close all connections first\n");
		pthread_mutex_unlock(&dpc_handle->lock);
		return false;
	}

	bool result = dpc_destroy_cmd(dpc_handle->handle) == 0;

	if (result) {
		log_debug(dpc_handle->debug, "dpc_destroy_cmd successful\n");
	}

	for (int i = 0; i < FUNQ_MAX_DMA_BUFFERS; i++) {
		if (!dpc_handle->buffers[i].dma_addr_local) continue;
		funq_dma_free(dpc_handle->handle, DMA_BUFSIZE_BYTES, dpc_handle->buffers[i].dma_addr_local, dpc_handle->buffers[i].dma_addr_dpu);
	}

	pthread_mutex_unlock(&dpc_handle->lock);
	free(dpc_handle);
	return result;
}

bool dpc_funq_send(struct dpc_funq_connection *connection, struct fun_ptr_and_size data)
{
	int allocations_n;
	int *allocations;

	if (!dpc_init_buffers(&allocations, &allocations_n, connection->dpc_handle, connection->send_buffer_idx)) {
		log_error("failed to init buffers, can't send\n");
		return false;
	}

	if (!connection->receiver_alive) {
		log_error("no receiver running, can't send\n");
		return false;
	}

	size_t position = 0;
	bool result = true;
	while (result && position < data.size) {
		dpc_reallocate_buffers(&allocations, &allocations_n, connection->dpc_handle,
			CEILING(data.size - position, DMA_BUFSIZE_BYTES));

		log_debug(connection->dpc_handle->debug, "allocated %d buffers\n", allocations_n);

		result = dpc_send_data_cmd(&position, connection, data, allocations, allocations_n);
	}

	dpc_free_buffers(allocations, allocations_n, connection->dpc_handle);
	return result;
}

bool dpc_funq_register_receive_callback(struct dpc_funq_connection *connection,
	dpc_funq_callback_t callback, void *context)
{
	pthread_mutex_lock(&connection->receive_lock);
	if (connection->receiver_alive) {
		log_error("receiver already running\n");
		pthread_mutex_unlock(&connection->receive_lock);
		return false;
	}
	connection->receiver_alive = true;
	connection->callback = callback;
	connection->callback_context = context;
	pthread_mutex_unlock(&connection->receive_lock);
	
	return dpc_first_recv_data_cmd(connection);
}

#else

struct dpc_funq_handle {
	void *handle;
};

struct dpc_funq_connection {
	struct dpc_funq_handle *h;
};

struct dpc_funq_handle *dpc_funq_init(const char *devname, bool debug)
{
	return NULL;
}

bool dpc_funq_destroy(struct dpc_funq_handle *dpc_handle)
{
	return false;
}

struct dpc_funq_connection *dpc_funq_open_connection(struct dpc_funq_handle *dpc_handle)
{
	return NULL;
}

extern bool dpc_funq_close_connection(struct dpc_funq_connection *connection)
{
	return false;
}

bool dpc_funq_send(struct dpc_funq_connection *connection, struct fun_ptr_and_size data)
{
	return false;
}

bool dpc_funq_register_receive_callback(struct dpc_funq_connection *connection,
	dpc_funq_callback_t callback, void *context)
{
	return false;
}

#endif
