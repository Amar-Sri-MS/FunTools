/*
 *  dpcsh_libfunq.h
 *
 *  Created by Shweta on 2018-02-12.
 *  Copyright © 2016 Fungible. All rights reserved.
 */

#pragma once

#include <pthread.h>
#include <FunSDK/nucleus/types.h>

#define FUNQ_DEV_NAME ("auto")
#define FUNQ_MAX_CONNECTIONS (63)
#define FUNQ_MAX_DMA_BUFFERS (126) // 128 - 2 (cq + sq)

typedef void (*dpc_funq_callback_t)(struct fun_ptr_and_size response, void *context);

struct dpc_funq_handle;
struct dpc_funq_connection;

// malloc and initialize a handle
extern bool dpc_funq_init(struct dpc_funq_handle **handle, const char *devname, bool debug);
// cleanup and free a handle
extern bool dpc_funq_destroy(struct dpc_funq_handle *handle);

extern bool dpc_funq_open_connection(struct dpc_funq_connection **connection, struct dpc_funq_handle *handle);
extern bool dpc_funq_close_connection(struct dpc_funq_connection *connection);

extern bool dpc_funq_send(struct dpc_funq_connection *connection, struct fun_ptr_and_size data);
extern bool dpc_funq_register_receive_callback(struct dpc_funq_connection *connection,
	dpc_funq_callback_t callback, void *context);
