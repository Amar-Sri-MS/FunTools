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
#define FUNQ_ASYNC_DEPTH (16)
#define FUNQ_MAX_DATA_BYTES (100*1024*1024)

typedef void (*dpc_funq_callback_t)(struct fun_ptr_and_size response, void *context);

struct dpc_funq_connection {
	void *handle;
	bool available[FUNQ_ASYNC_DEPTH];
	void *allocated[FUNQ_ASYNC_DEPTH];
	pthread_mutex_t lock;
	bool debug;
};

extern bool dpc_funq_init(struct dpc_funq_connection *c, const char *devname, bool debug);
extern bool dpc_funq_destroy(struct dpc_funq_connection *c);

extern bool dpc_funq_send(struct fun_ptr_and_size data, struct dpc_funq_connection *c,
	dpc_funq_callback_t callback, void *context);
