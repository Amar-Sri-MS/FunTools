#include "data-type-def-action.h"
#include "data-type-def-arg0.h"
#include "data-type-def-arg1.h"
#include "data-type-def-cmd-common.h"
#include "data-type-def-cmd-gather.h"
#include "data-type-def-cmd-scatter.h"
#include "data-type-def-cmd.h"

/* List of data types to decode */
static const struct data_type_def_s data_type_defs[] = {
	{'a',	"action",		action},
	{'0',	"DMA WU arg0",		dma_wu_arg0},
	{'1',	"DMA WU arg1",		dma_wu_arg1},
	{'c',	"DMA command",		dma_cmd},
	{'\0',	"",			NULL}
};
