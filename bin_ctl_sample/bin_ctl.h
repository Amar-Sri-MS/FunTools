/*
 *  TODO(ridrisov): move this to fungible-host-drivers
 *  bin_ctl.h
 *
 *  Created by Renat on 2021-09-12.
 *  Copyright © 2021 Fungible. All rights reserved.
 */

#pragma once

#include <pthread.h>
#include <FunSDK/nucleus/types.h>

#define FUNQ_DEV_NAME ("auto")
#define FUNQ_MAX_CONNECTIONS (63)
#define FUNQ_MAX_DMA_BUFFERS (126) // 128 - 2 (cq + sq)

// response ownership is transferred
typedef void (*bin_ctl_callback_t)(struct fun_ptr_and_size response, void *context);

struct bin_ctl_handle;
struct bin_ctl_connection;

// malloc and initialize a handle
extern struct bin_ctl_handle *bin_ctl_init(const char *devname, bool debug, uint16_t handler_id);
// call bin_ctl_init with dpc handler id
extern struct bin_ctl_handle *bin_ctl_init_dpc(const char *devname, bool debug);
// cleanup and free a handle
extern bool bin_ctl_destroy(struct bin_ctl_handle *handle);

extern struct bin_ctl_connection *bin_ctl_open_connection(struct bin_ctl_handle *handle);
extern bool bin_ctl_close_connection(struct bin_ctl_connection *connection);

extern bool bin_ctl_send(struct bin_ctl_connection *connection, struct fun_ptr_and_size data);

// returns number of items sent
extern size_t bin_ctl_send_batch(struct bin_ctl_connection *connection, struct fun_ptr_and_size *data, size_t n);
extern bool bin_ctl_register_receive_callback(struct bin_ctl_connection *connection,
	bin_ctl_callback_t callback, void *context);
