/*
 *  dpcsh_libfunq.c
 *
 *  Created by Shweta on 2018-02-12.
 *  Copyright © 2016 Fungible. All rights reserved.
 */

#include <stdio.h>
#include <unistd.h>
#include "dpcsh_libfunq.h"

// libfunq is supported only for Linux
#ifdef WITH_LIBFUNQ
#include "libfunq.h"

#define DMA_BUFSIZE_BYTES 	(16384)
#define ASQE_SIZE			(256)
#define ACQE_SIZE			(256)
#define ASQ_DEPTH			(DMA_BUFSIZE_BYTES / ASQE_SIZE)
#define ACQ_DEPTH			(DMA_BUFSIZE_BYTES / ACQE_SIZE)
#define FIRST_LEVEL_SGL_N			(12)

#define RET_NEED_BUFFER	(3)
#define RET_FAIL	(1)
#define RET_OK	(0)

static_assert(DMA_BUFSIZE_BYTES / sizeof(struct fun_subop_sgl) * FIRST_LEVEL_SGL_N * DMA_BUFSIZE_BYTES > FUNQ_MAX_DATA_BYTES, "Must be enough space for buffer descriptors");
static_assert((FUNQ_ASYNC_DEPTH <= ASQ_DEPTH) && (FUNQ_ASYNC_DEPTH <= ACQ_DEPTH), "Queue must be deep enough to support all the context");

#define CEILING(x,y) (((x) + (y) - 1) / (y))
#define SECOND_LEVEL_SGL_N (CEILING(FUNQ_MAX_DATA_BYTES, DMA_BUFSIZE_BYTES))

struct dpc_direct_context {
	struct dpc_funq_connection *connection;
	struct fun_admin_dpc_req *c;

	dpc_funq_callback_t callback;
	void *callback_context;

	size_t out_sgl_n;
	void *dma_addr_local[FIRST_LEVEL_SGL_N];
	dma_addr_t dma_addr_dpu[FIRST_LEVEL_SGL_N];
};

struct dpc_2level_context {
	struct dpc_direct_context *first_level;

	size_t sgl_n;
	size_t out_sgl_n;
	void *dma_addr_local[SECOND_LEVEL_SGL_N];
	dma_addr_t dma_addr_dpu[SECOND_LEVEL_SGL_N];
};

static int dpc_get_last(struct dpc_direct_context *context, size_t size, uint8_t result_id);

static int dpc_create_cmd(funq_handle_t *handle)
{
	struct fun_admin_dpc_req *c = NULL;
	struct fun_admin_dpc_rsp *r = NULL;
	int rc = -ENOMEM;

	c = calloc(1, sizeof(*c));
	r = calloc(1, sizeof(*r));

	if (!c || !r) {
		rc = -ENOMEM;
		goto done;
	}

	fun_admin_req_common_init(&c->common, FUN_ADMIN_OP_DPC,
			sizeof (*c) >> 3, 0 /* flags */, 0 /* suboff8 */, 0 /* cid */);
	fun_admin_dpc_create_req_init(c, FUN_ADMIN_SUBOP_CREATE,
			FUN_ADMIN_RES_CREATE_FLAG_ALLOCATOR /* flag */, 0 /* id */);

	rc = funq_admin_submit_sync_cmd(*handle,
			&c->common, &r->common, sizeof(*r), 0);

done:
	free(r);
	free(c);
	return rc;
}

static struct fun_ptr_and_size dpc_get_response_data(size_t size,
	void **dma_addr_local, size_t nsgl, size_t out_sgl_n)
{
	struct fun_ptr_and_size p;
	size_t position = 0;

	p.size = size;
	p.ptr = (uint8_t *)malloc(p.size);

	for (size_t i = out_sgl_n; i < out_sgl_n + nsgl && position < p.size; i++) {
		memcpy(p.ptr + position, dma_addr_local[i],
			min((size_t)DMA_BUFSIZE_BYTES, p.size - position));
		position += DMA_BUFSIZE_BYTES;
	}
	return p;
}

static void dpc_process_release_direct_context(struct dpc_direct_context *context)
{
	for (size_t i = 0; i < FUNQ_ASYNC_DEPTH; i++) {
		if (context->connection->allocated[i] == context) {
			if (context->connection->debug) {
				printf("Releasing libfunq request context #%zu\n", i);
			}
			context->connection->available[i] = true;
			break;
		}
	}
}

static void dpc_process_direct_response(void *response, void *ctx)
{
	struct dpc_direct_context *context = ctx;
	struct fun_admin_dpc_rsp *r = response;
	struct fun_ptr_and_size p;

	if (r->u.issue_cmd.code == RET_NEED_BUFFER) {
		dpc_get_last(context, r->u.issue_cmd.resp_size, r->u.issue_cmd.result_id);
		return;
	}
	size_t nsgl = ((r->common.len8 << 3) - sizeof(*r))/sizeof(struct fun_subop_sgl);


	p = dpc_get_response_data(r->u.issue_cmd.resp_size, context->dma_addr_local, nsgl, context->out_sgl_n);

	pthread_mutex_lock(&context->connection->lock);
	context->callback(p, context->callback_context);

	dpc_process_release_direct_context(context);
	free(p.ptr);
	pthread_mutex_unlock(&context->connection->lock);
}

// direct part is not affected by this call
static void dpc_deallocate_2level_context(struct dpc_2level_context *context)
{
	if (context) {
		funq_handle_t *handle = context->first_level->connection->handle;
		for (size_t i = 0; i < context->sgl_n; i++) {
			if (!context->dma_addr_local[i]) continue;
			funq_dma_free(*handle, DMA_BUFSIZE_BYTES, context->dma_addr_local[i], context->dma_addr_dpu[i]);
		}
	}
	free(context);
}

static void dpc_process_2level_response(void *response, void *ctx)
{
	struct dpc_2level_context *context = ctx;
	struct dpc_direct_context *direct = context->first_level;
	struct fun_admin_dpc_rsp *r = response;
	struct fun_ptr_and_size p;

	if (r->u.issue_cmd.code == RET_NEED_BUFFER) {
		dpc_deallocate_2level_context(context);
		dpc_get_last(direct, r->u.issue_cmd.resp_size, r->u.issue_cmd.result_id);
		return;
	}

	p = dpc_get_response_data(r->u.issue_cmd.resp_size, context->dma_addr_local,
		context->sgl_n - context->out_sgl_n, context->out_sgl_n);

	pthread_mutex_lock(&direct->connection->lock);

	direct->callback(p, direct->callback_context);
	free(p.ptr);

	dpc_deallocate_2level_context(context);
	dpc_process_release_direct_context(direct);

	pthread_mutex_unlock(&direct->connection->lock);
}

static void dpc_deallocate_context(struct dpc_direct_context *context)
{
	if (context) {
		free(context->c);
		funq_handle_t *handle = context->connection->handle;
		for (size_t i = 0; i < FIRST_LEVEL_SGL_N; i++) {
			if (!context->dma_addr_local[i]) continue;
			funq_dma_free(*handle, DMA_BUFSIZE_BYTES, context->dma_addr_local[i], context->dma_addr_dpu[i]);
		}
	}
	free(context);
}

static void dpc_allocate_direct_context(struct dpc_funq_connection *connection, size_t n)
{
	struct dpc_direct_context *context = (struct dpc_direct_context *)calloc(1, sizeof(struct dpc_direct_context));
	connection->allocated[n] = context;
	context->connection = connection;
	funq_handle_t *handle = connection->handle;

	if (!context) {
		return;
	}

	size_t total_sgl_len = sizeof(struct fun_subop_sgl) * FIRST_LEVEL_SGL_N;
	context->c = calloc(1, sizeof(*context->c) + total_sgl_len);

	if (!context->c) {
		goto fail;
	}

	for (size_t i = 0; i < FIRST_LEVEL_SGL_N; i++) {
		context->dma_addr_local[i] = (uint8_t *)funq_dma_alloc(*handle, DMA_BUFSIZE_BYTES, &context->dma_addr_dpu[i]);
		if (!context->dma_addr_local[i]) goto fail;
	}
	return;

fail:
	dpc_deallocate_context(context);
	connection->allocated[n] = NULL;
}

static struct dpc_2level_context *dpc_allocate_2level_context(struct dpc_direct_context *first_level, size_t input_size, size_t output_size)
{
	struct dpc_2level_context *context =
		(struct dpc_2level_context *)calloc(1, sizeof(struct dpc_2level_context));

	if (!context) return NULL;

	context->first_level = first_level;
	funq_handle_t *handle = first_level->connection->handle;
	context->out_sgl_n = CEILING(input_size, DMA_BUFSIZE_BYTES);
	context->sgl_n = context->out_sgl_n + CEILING(output_size, DMA_BUFSIZE_BYTES);

	for (size_t i = 0; i < context->sgl_n; i++) {
		context->dma_addr_local[i] = (uint8_t *)funq_dma_alloc(*handle, DMA_BUFSIZE_BYTES, &context->dma_addr_dpu[i]);
		if (!context->dma_addr_local[i]) goto fail;
	}

	for (size_t i = 0; i < context->sgl_n; i++) {
		size_t first_level_index = i * sizeof(struct fun_subop_sgl) / DMA_BUFSIZE_BYTES;
		size_t first_level_offset = i - first_level_index * (DMA_BUFSIZE_BYTES / sizeof(struct fun_subop_sgl));
		struct fun_subop_sgl *buffer = context->first_level->dma_addr_local[first_level_index];
		fun_subop_sgl_init(buffer + first_level_offset, i < context->out_sgl_n ? FUN_DATAOP_GL : FUN_DATAOP_SL, 0, 1,
			DMA_BUFSIZE_BYTES, cpu_to_dpu64((uint64_t)context->dma_addr_dpu[i]));
	}

	return context;
fail:
	dpc_deallocate_2level_context(context);
	return NULL;
}

static void init_request_header(struct dpc_direct_context *context, bool direct, size_t size)
{
	size_t total_sgl_len = sizeof(struct fun_subop_sgl) * FIRST_LEVEL_SGL_N;
	struct fun_subop_sgl *sgl = context->c->sgl;

	//setup common admin and dpc specific reqs
	fun_admin_req_common_init(&context->c->common,
			FUN_ADMIN_OP_DPC, (sizeof(*context->c)+total_sgl_len) >> 3,
			0 /* flags */, 0 /* suboff8 */, 0 /* cid */);
	fun_admin_dpc_issue_cmd_req_init(context->c,
			FUN_ADMIN_DPC_SUBOP_EXECUTE_CMD,
			0 /* flag */, 0 /* id */, cpu_to_dpu64(size));

	context->out_sgl_n = CEILING(size, DMA_BUFSIZE_BYTES);
	for (size_t i = 0; i < FIRST_LEVEL_SGL_N; i++) {
		fun_subop_sgl_init(sgl + i,
			direct ? (i < context->out_sgl_n ? FUN_DATAOP_GL : FUN_DATAOP_SL) : FUN_DATAOP_INDIRECT,
			0 /* flags */, 1 /* nsgl */, DMA_BUFSIZE_BYTES /* sgl_len */,
			cpu_to_dpu64((uint64_t)context->dma_addr_dpu[i]) /* sgl_data */);
	}
}

static void fill_sgl_buffers(void **local_data, struct fun_ptr_and_size data)
{
	size_t output_buffers_n = CEILING(data.size, DMA_BUFSIZE_BYTES);
	for (size_t index = 0; index < output_buffers_n; index++) {
		memcpy(local_data[index], data.ptr + index * DMA_BUFSIZE_BYTES, min((size_t)DMA_BUFSIZE_BYTES, data.size - index * DMA_BUFSIZE_BYTES));
	}
}

static int dpc_issue_direct_cmd(struct dpc_direct_context *context, struct fun_ptr_and_size data)
{
	funq_handle_t *handle = context->connection->handle;
	init_request_header(context, true, data.size);

	fill_sgl_buffers(context->dma_addr_local, data);

	return funq_admin_submit_async_cmd(*handle,
			&context->c->common, dpc_process_direct_response, sizeof(struct fun_admin_dpc_rsp), context);
}

static int dpc_issue_2level_cmd(struct dpc_2level_context *context, struct fun_ptr_and_size data)
{
	funq_handle_t *handle = context->first_level->connection->handle;
	init_request_header(context->first_level, false, data.size);

	fill_sgl_buffers(context->dma_addr_local, data);

	return funq_admin_submit_async_cmd(*handle,
			&context->first_level->c->common, dpc_process_2level_response, sizeof(struct fun_admin_dpc_rsp), context);
}

static void init_get_last_request_header(struct dpc_direct_context *context, bool direct, uint8_t result_id)
{
	init_request_header(context, direct, 1);
	fun_admin_dpc_get_last_req_init(context->c,
		FUN_ADMIN_DPC_SUBOP_GET_RESULT_CMD,
		result_id, 0, 0 /* id */);
}

static int dpc_issue_direct_get_last(struct dpc_direct_context *context, uint8_t result_id)
{
	funq_handle_t *handle = context->connection->handle;

	init_get_last_request_header(context, true, result_id);
	return funq_admin_submit_async_cmd(*handle,
			&context->c->common, dpc_process_direct_response, sizeof(struct fun_admin_dpc_rsp), context);
}

static int dpc_issue_2level_get_last(struct dpc_2level_context *context, uint8_t result_id)
{
	funq_handle_t *handle = context->first_level->connection->handle;

	init_get_last_request_header(context->first_level, false, result_id);
	return funq_admin_submit_async_cmd(*handle,
			&context->first_level->c->common, dpc_process_2level_response, sizeof(struct fun_admin_dpc_rsp), context);
}

static int dpc_issue_cmd(struct dpc_direct_context *context, struct fun_ptr_and_size data,
	dpc_funq_callback_t callback, void *callback_context)
{
	context->callback = callback;
	context->callback_context = callback_context;
	if (data.size > (FIRST_LEVEL_SGL_N - 1) * DMA_BUFSIZE_BYTES) {
		struct dpc_2level_context *c = dpc_allocate_2level_context(context, data.size, 1);
		return dpc_issue_2level_cmd(c, data);
	}
	return dpc_issue_direct_cmd(context, data);
}

static int dpc_get_last(struct dpc_direct_context *context, size_t size, uint8_t result_id)
{
	if (size > (FIRST_LEVEL_SGL_N - 1) * DMA_BUFSIZE_BYTES) {
		struct dpc_2level_context *c = dpc_allocate_2level_context(context, 0, size);
		return dpc_issue_2level_get_last(c, result_id);
	}
	return dpc_issue_direct_get_last(context, result_id);
}

int dpc_destroy_cmd(funq_handle_t *handle)
{
	struct fun_admin_dpc_req *c = NULL;
	struct fun_admin_dpc_rsp *r = NULL;
	int rc = -ENOMEM;

	c = calloc(1, sizeof(*c));
	r = calloc(1, sizeof(*r));

	if (!r || !c) {
		rc = -ENOMEM;
		goto done;
	}

	fun_admin_req_common_init(&c->common, FUN_ADMIN_OP_DPC,
			sizeof (*c) >> 3, 0 /* flags */, 0 /* suboff8 */, 0 /* cid */);
	fun_admin_dpc_destroy_req_init(c, FUN_ADMIN_SUBOP_DESTROY,
			0 /* flag */, 0 /* id */);

	rc = funq_admin_submit_sync_cmd(*handle,
			&c->common, &r->common, sizeof(*r), 0);

done:
	free(r);
	free(c);
	return rc;
}

funq_handle_t *dpc_admin_queue_init(const char *devname)
{
	funq_handle_t *handle;
	int rc;

	handle = (funq_handle_t *)malloc(sizeof(funq_handle_t));


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

	/* devname NULL = auto discover */
	rc = funq_admin_init(DEVTYPE_VFIO, devname_p, &aqreq, handle);

	if (rc) {
		printf("err: funq_admin_init failed\n");
		exit(rc);
	}

	return handle;
}

bool dpc_funq_init(struct dpc_funq_connection *c, const char *devname, bool debug)
{
	bzero(c, sizeof(struct dpc_funq_connection));
	c->debug = debug;

	if (pthread_mutex_init(&c->lock, NULL) != 0) {
		printf("err: failed to initialize pthread mutex\n");
		return false;
	}

	c->handle = dpc_admin_queue_init(devname);
	if (c->handle == NULL) return false;

	return dpc_create_cmd(c->handle) == 0;
}

bool dpc_funq_destroy(struct dpc_funq_connection *c)
{
	pthread_mutex_lock(&c->lock);
	for (size_t i = 0; i < FUNQ_ASYNC_DEPTH; i++) {
		dpc_deallocate_context(c->allocated[i]);
	}

	bool result = dpc_destroy_cmd(c->handle) == 0;
	pthread_mutex_unlock(&c->lock);
	return result;
}

bool dpc_funq_send(struct fun_ptr_and_size data, struct dpc_funq_connection *c,
	dpc_funq_callback_t callback, void *context)
{
	pthread_mutex_lock(&c->lock);
	int index = -1;
	for (size_t i = 0; i < FUNQ_ASYNC_DEPTH; i++) {
		if (c->available[i]) {
			index = (int)i;
			break;
		}
		if (c->allocated[i] == NULL) {
			index = (int)i;
			printf("Allocating libfunq request context #%zu\n", i);
			dpc_allocate_direct_context(c, i);
			break;
		}
	}

	if (index == -1 || c->allocated[(size_t)index] == NULL) {
		pthread_mutex_unlock(&c->lock);
		return false;
	}

	size_t good_index = (size_t)index;

	if (c->debug) {
		printf("Using libfunq request context #%zu\n", good_index);
	}

	c->available[good_index] = false;
	bool result = dpc_issue_cmd(c->allocated[good_index], data, callback, context) == 0;
	if (!result) {
		if (c->debug) {
			printf("Releasing libfunq request context #%zu\n", good_index);
		}
		c->available[good_index] = true;
	}
	pthread_mutex_unlock(&c->lock);
	return result;
}

#else

bool dpc_funq_init(struct dpc_funq_connection *c, const char *devname, bool debug)
{
	return false;
}

bool dpc_funq_destroy(struct dpc_funq_connection *c)
{
	return false;
}

bool dpc_funq_send(struct fun_ptr_and_size data, struct dpc_funq_connection *c,
	dpc_funq_callback_t callback, void *context)
{
	return false;
}

#endif
