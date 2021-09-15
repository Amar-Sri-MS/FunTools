/*
 *  dpcsh_ptr_queue.c
 *
 *  Created by Renat Idrisov on 2021-08-29.
 *  Copyright © 2021 Fungible. All rights reserved.
 */

#include "dpcsh_ptr_queue.h"

#include <stdlib.h>
#define MIN_QUEUE_SIZE (16)

struct dpcsh_ptr_queue *dpcsh_ptr_queue_new()
{
	return calloc(1, sizeof(struct dpcsh_ptr_queue));
}

void dpcsh_ptr_queue_delete(struct dpcsh_ptr_queue *q)
{
	dpcsh_ptr_queue_dequeue(q, q->last - q->first);

	free(q->buffer);
	free(q->owners);
	free(q);
}

static void dpcsh_ptr_queue_set_advance(struct dpcsh_ptr_queue *q,
	struct fun_ptr_and_size element, void *owner)
{
	q->owners[q->last] = owner;
	q->buffer[q->last++] = element;
}

bool dpcsh_ptr_queue_enqueue(struct dpcsh_ptr_queue *q,
	struct fun_ptr_and_size element, void *owner)
{
	if (q->last < q->allocated) {
		dpcsh_ptr_queue_set_advance(q, element, owner);
		return true;
	}
	if (q->first > 0) {
		for (size_t i = 0; i < q->last - q->first; i++) {
			q->buffer[i] = q->buffer[q->first + i];
			q->owners[i] = q->owners[q->first + i];
		}
		q->last -= q->first;
		q->first = 0;
		dpcsh_ptr_queue_set_advance(q, element, owner);
		return true;
	}

	if (!q->allocated) q->allocated = MIN_QUEUE_SIZE;
	else q->allocated *= 2;

	struct fun_ptr_and_size *new_buffer = realloc(q->buffer, sizeof(struct fun_ptr_and_size) * q->allocated);
	void *new_owners = realloc(q->owners, sizeof(void *) * q->allocated);
	if (!new_buffer || !new_owners) {
		free(new_owners);
		free(new_buffer);
		return false;
	}

	q->buffer = new_buffer;
	q->owners = new_owners;
	dpcsh_ptr_queue_set_advance(q, element, owner);
	return true;
}

struct fun_ptr_and_size *dpcsh_ptr_queue_first(struct dpcsh_ptr_queue *q)
{
	return q->buffer + q->first;
}

size_t dpcsh_ptr_queue_size(struct dpcsh_ptr_queue *q)
{
	return q->last - q->first;
}

bool dpcsh_ptr_queue_dequeue(struct dpcsh_ptr_queue *q, size_t n)
{
	if (q->first + n > q->last) return false;

	for (size_t i = q->first; i < q->first + n; i++) {
		if ((i + 1) == q->last || q->owners[i] != q->owners[i + 1])
			free(q->owners[i]);
	}

	q->first += n;
	return true;
}