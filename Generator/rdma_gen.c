// Header created by generator.py
// Do not change this file;
// change the gen file "examples/rdma.gen" instead.


#include <stdint.h>
#include <assert.h>
#include "rdma_gen.h"

const char *source_names[] = {
	"SOURCE_HOST",  /* 0x0 */
	"SOURCE_F1",  /* 0x1 */
	"SOURCE_GENERATE",  /* 0x2 */
};
const char *opcode_names[] = {
	"OPCODE_GATHER",  /* 0x0 */
	"OPCODE_OPERATE",  /* 0x1 */
	"OPCODE_SCATTER",  /* 0x2 */
};
/* Definitions for flag set Mask */
const int EMPTY = 0x0;
const int FOO = 0x1;
const int BAR = 0x2;
const int BAZ = 0x4;
const int BAR_AND_BAZ = 0x6;

const char *Mask_names[3] = {
	"FOO",  /* 0x1 */ 
	"BAR",  /* 0x2 */ 
	"BAZ",  /* 0x4 */ 
};

void WorkUnit_init(struct WorkUnit *s, uint8_t destinationID, uint8_t sourceID, uint16_t frameSize, uint32_t listSize, uint64_t flowPtr, uint64_t packetPtr) {
	s->destinationID = destinationID;
	s->sourceID = sourceID;
	s->frameSize = frameSize;
	s->listSize = listSize;
	s->flowPtr = flowPtr;
	s->packetPtr = packetPtr;
}
void GatherListInlineFragment_init(struct GatherListFragmentHeader *s, uint8_t opcode, uint8_t source, uint8_t inlineByteCount) {
	assert(opcode < 0x4);
	assert(source < 0x4);
	assert(inlineByteCount < 0x10);
	s->u1.inline_cmd.opcode = opcode;
	s->u1.inline_cmd.source = source;
	s->u1.inline_cmd.inlineByteCount = inlineByteCount;
}
void GatherListGenerateFragment_init(struct GatherListFragmentHeader *s, uint8_t opcode, uint8_t source, uint64_t bytesToGenerate, uint64_t pattern0) {
	assert(opcode < 0x4);
	assert(source < 0x4);
	assert(bytesToGenerate < 0x100000000000000);
	s->u1.generate_cmd.opcode = opcode;
	s->u1.generate_cmd.source = source;
	s->u1.generate_cmd.bytesToGenerate = bytesToGenerate;
	s->u1.generate_cmd.pattern0 = pattern0;
}
void GatherListOperateFragment_init(struct GatherListFragmentHeader *s, uint8_t opcode, uint8_t source, uint8_t sizeOfData) {
	assert(opcode < 0x4);
	assert(source < 0x40);
	s->u1.operate_cmd.opcode = opcode;
	s->u1.operate_cmd.source = source;
	s->u1.operate_cmd.sizeOfData = sizeOfData;
}
void GatherListScatterFragment_init(struct GatherListFragmentHeader *s, uint8_t opcode, uint8_t destination, uint8_t instance, uint16_t length, uint32_t info, uint64_t address) {
	assert(opcode < 0x4);
	assert(destination < 0x4);
	assert(instance < 0x4);
	s->u1.scatter_cmd.opcode = opcode;
	s->u1.scatter_cmd.destination = destination;
	s->u1.scatter_cmd.instance = instance;
	s->u1.scatter_cmd.length = length;
	s->u1.scatter_cmd.info = info;
	s->u1.scatter_cmd.address = address;
}
void MultiFlitField_init(struct MultiFlitField *s, uint8_t cmd, uint32_t end) {
	s->cmd = cmd;
	s->end = end;
}
