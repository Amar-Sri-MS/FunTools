/*
 *  dpcsh_ptr_queue.h
 *
 *  Created by Renat Idrisov on 2021-08-29.
 *  Copyright © 2021 Fungible. All rights reserved.
 */

#pragma once
#include <stddef.h>
#include <FunOS/nucleus/types.h>

struct dpcsh_ptr_queue {
	struct fun_ptr_and_size *buffer;
	void **owners;
	size_t allocated;
	size_t first;
	size_t last;

	size_t complete_size;
};

// get a new empty queue
struct dpcsh_ptr_queue *dpcsh_ptr_queue_new();

// deallocate both queue and any enqueued elements
void dpcsh_ptr_queue_delete(struct dpcsh_ptr_queue *q);

// add element to the queue, grow queue if needed, ownership transferred
// the assumption is that all elements belonging to owner block are added sequentially
// with no dequeue in between
bool dpcsh_ptr_queue_enqueue(struct dpcsh_ptr_queue *q, struct fun_ptr_and_size element, void *owner);

// point to the first element, NULL if none
struct fun_ptr_and_size *dpcsh_ptr_queue_first(struct dpcsh_ptr_queue *q);

// get number of enqueued elements
size_t dpcsh_ptr_queue_size(struct dpcsh_ptr_queue *q);

// remove n elements from the queue, deallocate owner once the last of its elements got dequeued
bool dpcsh_ptr_queue_dequeue(struct dpcsh_ptr_queue *q, size_t n);