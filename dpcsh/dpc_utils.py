##
##  dpc_utils.py
##
##  Various utils / helpers for DPC
##
##  Created by Charles Gray on 2022-07-20
##  Copyright (C) 2022 Fungible. All rights reserved.
##

# Wait for a "FUNOS_STATUS" notification from FunOS
def wait_for_online(conn, timeout):
    while(True):
        r = conn.async_recv_wait(-1, custom_timeout=True,
                                 timeout_seconds=timeout)

        if (r is None):
            raise RuntimeError("FunOS online timeout")

        # pend any other messages backon the connection
        if ("FUNOS_STATUS" not in r):
            conn.__async_queue.append(r)
        else:
            break

    return r["FUNOS_STATUS"]
