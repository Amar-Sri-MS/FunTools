// Header created by generator.py
// Do not change this file;
// change the gen file "examples/rdma.gen" instead.

#ifndef __RDMA_GEN_H__
#define __RDMA_GEN_H__
#include "stdlib.h"
#include "stdint.h"

enum Source {
	SOURCE_HOST = 0x0,
	SOURCE_F1 = 0x1,
	SOURCE_GENERATE = 0x2, /* Generate data from pattern. */
	/* Remaining values refer to a specific VP. */
};

/* Human-readable strings for enum values in Source. */
extern const char *source_names[];

enum Opcode {
	OPCODE_GATHER = 0x0,
	OPCODE_OPERATE = 0x1,
	OPCODE_SCATTER = 0x2,
};

/* Human-readable strings for enum values in Opcode. */
extern const char *opcode_names[];

/* Declarations for flag set Mask */
/* Bitfield for some unknown purpose. */
const int EMPTY;  /* 0x0 */
const int FOO;  /* 0x1 */
	/* Body comment. */
const int BAR;  /* 0x2, Key comment. */
const int BAZ;  /* 0x4 */
	/* Bitfields can include both single bits and groups. */
const int BAR_AND_BAZ;  /* 0x6 */

/* String names for all power-of-two flags in Mask. */
const char *Mask_names[3];

/*
 * Standard Work Unit format for all messages in F1.
 * Work units are the standard unit of computation inside the F1
 * chip, and can be sent by any unit.
 */
struct WorkUnit {
	uint8_t destinationID; /* DMA engine WU queue */
	uint8_t sourceID; /* Source (VP or hardware block) */
	uint16_t frameSize; /* number of 64B blocks referenced by frame ptr */
	uint32_t listSize; /* number of 16B blocks contained in command list. */

	uint64_t flowPtr; /* Usually reference to the flow data structure. */

	uint64_t packetPtr; /* Usually reference to payload to process. */

	uint64_t reserved2;
/* WorkUnits are always 32 bytes. */
};

/* Fragment descriptor pointing to a 16 byte gather entry. */
struct GatherListFragmentHeader {
		union Command {
				/*
		 * GatherListFragment for 16 byte unit specifying bytes to insert
		 * at current offset
		 */
		struct GatherListInlineFragment {
			uint8_t opcode:2;
			uint8_t source:2; /* will be OPCODE_GATHER */
			uint8_t inlineByteCount:4;
			uint8_t bytes[15]; /* First seven bytes of inline copy. */
		} inline_cmd;
				/* Generate bytes from pattern. */
		struct GatherListGenerateFragment {
			uint8_t opcode:2;
			uint8_t source:2; /* will be SOURCE_GENERATE */
			uint8_t reserved:4;
			uint64_t bytesToGenerate:56;

			uint64_t pattern0;
		} generate_cmd;
				/* Generate bytes from pattern. opcode will be OPCODE_OPERATE. */
		struct GatherListOperateFragment {
			uint8_t opcode:2;
			uint8_t source:6; /* accelerator number and function number. */
			uint8_t sizeOfData; /* in 8B words in addition to current 8B */
		/* Followed by 6-126B of data. */
		} operate_cmd;
				/* Scatter data. Opcode will be OPCODE_SCATTER */
		struct GatherListScatterFragment {
			uint8_t opcode:2;
			uint8_t destination:2;
			uint8_t instance:2;
			uint8_t reserved:2;
			uint16_t length; /* byte length of fragment */
			uint32_t info; /* metadata */

			uint64_t address; /* byte-aligned physical address of destination fragment. */
		} scatter_cmd;
	} u1;
};

struct MultiFlitField {
	uint8_t cmd;
	uint8_t buf[19];

	uint32_t end;
};
extern void WorkUnit_init(struct WorkUnit *s, uint8_t destinationID, uint8_t sourceID, uint16_t frameSize, uint32_t listSize, uint64_t flowPtr, uint64_t packetPtr);

extern void GatherListInlineFragment_init(struct GatherListFragmentHeader *s, uint8_t opcode, uint8_t source, uint8_t inlineByteCount);

extern void GatherListGenerateFragment_init(struct GatherListFragmentHeader *s, uint8_t opcode, uint8_t source, uint64_t bytesToGenerate, uint64_t pattern0);

extern void GatherListOperateFragment_init(struct GatherListFragmentHeader *s, uint8_t opcode, uint8_t source, uint8_t sizeOfData);

extern void GatherListScatterFragment_init(struct GatherListFragmentHeader *s, uint8_t opcode, uint8_t destination, uint8_t instance, uint16_t length, uint32_t info, uint64_t address);

extern void MultiFlitField_init(struct MultiFlitField *s, uint8_t cmd, uint32_t end);

#endif // __RDMA_GEN_H__