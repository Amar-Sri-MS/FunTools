#!/bin/sh

args="-l .c"

if [ $# -eq 0 ]; then
    echo "usage: $0 [--rewrite] <files>"
    exit 1
fi

if [ $1 == "--rewrite" ]; then
        echo "Re-writing files as we go"
        args="${args} -in-place"
        shift
fi


for fname in "$@"; do
        echo "Processing ${fname}"

        # replace the header include
        comby ${args} '#include <generated/wu_ids.h>' '#include <nucleus/wu_register.h>' ${fname}

        # CHANNEL() with no attributes
        comby ${args} 'CHANNEL() void :[name](:[params])' 'CHANNEL_HANDLER(:[name], WU_ATTR_NONE, :[params])' ${fname}

        # CHANNEL(WU_ATTR...) with attributes
        comby ${args} 'CHANNEL(:[[attrs]]) void :[name](:[params])' 'CHANNEL_HANDLER(:[name], :[attrs], :[params])' ${fname}

        # CHANNEL_THREAD() with no attributes
        comby ${args} 'CHANNEL_THREAD() void :[name](:[params])' 'CHANNEL_THREAD(:[name], WU_ATTR_NONE, :[params])' ${fname}

        # CHANNEL_THREAD(WU_ATTR...) with attributes
        comby ${args} 'CHANNEL_THREAD(:[[attrs]]) void :[name](:[params])' 'CHANNEL_THREAD(:[name], :[attrs], :[params])' ${fname}

        # WU_HANDLER() with no attributes
        comby ${args} 'WU_HANDLER() void :[name](:[params])' 'WU_HANDLER(:[name], WU_ATTR_NONE, :[params])' ${fname}

        # WU_HANDLER(WU_ATTR...) with no attributes
        comby ${args} 'WU_HANDLER(:[[attrs]]) void :[name](:[params])' 'WU_HANDLER(:[name], :[attrs], :[params])' ${fname}

done

