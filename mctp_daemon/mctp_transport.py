#!/usr/bin/env python3
##
##  mctp_transport.py
##
##  Created by Karnik Jain on 2022-01-07
##  Copyright (C) 2022 Fungible. All rights reserved.
##

import json
import sys
import threading
import time
import tempfile
import stat, os
import argparse
import logging as log

parser = argparse.ArgumentParser()
parser.add_argument( '-log',
                     '--loglevel',
                     default='info',
                     help='Provide logging level. Example --loglevel debug, default=info' )
args = parser.parse_args()
log.basicConfig(filename='/tmp/mctp_transport.py.log',
                level=args.loglevel.upper(),
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

dpcsh_dir = '/usr/bin/'
sys.path.append(dpcsh_dir)
import dpc_client

######################################
PCIEVDM_TX_FIFO = '/tmp/mctp_pcie_tx'
PCIEVDM_RX_FIFO = '/tmp/mctp_pcie_rx'

#PLDM/MCTP Packet Egress Path
def mctp_pkt_tx():
    log.info("Started a thread to send PLDM/MCTP Pkts to HostServer ...")
    try:
        mctp_tx_dpc_handle = dpc_client.DpcClient(unix_sock = True)
        with open(PCIEVDM_TX_FIFO, 'rb') as pcievdm_tx_fifo:
            log.info("PCIEVDM_TX_FIFO opened")
            while True:
                mctp_pkt_tx_data = pcievdm_tx_fifo.read()
                if len(mctp_pkt_tx_data) == 0:
                    continue

                log.debug('Read data from FIFO before Bin -> Blob conversion: %s', mctp_pkt_tx_data)
                data = mctp_tx_dpc_handle.blob_from_string(mctp_pkt_tx_data)

                #Sending Data to HostServer using FunOS PCIe Driver
                result = mctp_tx_dpc_handle.execute('mctp_transport', ['mctp_hu_send', ['quote', data]])
                log.debug("'mctp_hu_send' packet DPCSH response: {}".format(result))
    except Exception as e:
        pcievdm_tx_fifo.close()
        result = mctp_tx_dpc_handle.execute("mctp_transport", ['mctp_hu_recv_unsub', 0])
        log.exception(" mctp_pkt_tx() failed, error:{}".format(e))
  
#PLDM/MCTP Packet Ingress Path
def mctp_pkt_rx():
    log.info("Started a thread to receive PLDM/MCTP Pkts to HostServer ...")

    try:
        mctp_rx_dpc_handle = dpc_client.DpcClient(unix_sock = True)
        tid = mctp_rx_dpc_handle.async_send("mctp_transport", "mctp_hu_recv_sub")

        result = mctp_rx_dpc_handle.async_recv_wait(tid)
        log.info("MCTP Rx Channel Successfully established: {}".format(result))

        with open(PCIEVDM_RX_FIFO, 'wb') as pcievdm_rx_fifo:
            log.info("PCIEVDM_RX_FIFO opened")
            while True:
                log.debug("Waiting for MCTP Packet from Host Server ........")
                result = mctp_rx_dpc_handle.async_recv_wait(tid)
                log.debug("MCTP async_recv_wait recieved response: {}".format(result))

                log.debug('Read data from Host Server: %s', result['data'])
                mctp_pkt_rx_data = mctp_rx_dpc_handle.blob_to_string(result['data'])
                log.debug('Read data from FIFO after Blob -> Binary conversion: %s', mctp_pkt_rx_data)

                pcievdm_rx_fifo.write(mctp_pkt_rx_data)

    except Exception as e:
        pcievdm_rx_fifo.close()
        result = mctp_rx_dpc_handle.execute("mctp_transport", ['mctp_hu_recv_unsub', 0])
        log.exception("mctp_pkt_rx() failed, error:{}".format(e))

# Main Function of MCTP Transport CCLinux GlueLayer
def main():

    try:
        log.info("Waiting for the MCTP Daemon to Start............")
        while True:
            if not os.path.exists(PCIEVDM_TX_FIFO):
                continue
            elif not os.path.exists(PCIEVDM_RX_FIFO):
                continue
            elif not stat.S_ISFIFO(os.stat(PCIEVDM_TX_FIFO).st_mode):
                continue
            elif not stat.S_ISFIFO(os.stat(PCIEVDM_RX_FIFO).st_mode):
                continue
            else:
                break

        log.info("Starting MCTP Transport CCLinux GlueLayer .....")
        # creating mctp_pkt_tx/rx threads
        mctp_pkt_rx_thread = threading.Thread(target=mctp_pkt_rx)
        mctp_pkt_tx_thread = threading.Thread(target=mctp_pkt_tx)
  
        # starting mctp_pkt_rx
        mctp_pkt_rx_thread.start()
        # starting mctp_pkt_tx
        mctp_pkt_tx_thread.start()
  
        # wait until mctp_pkt_rx is completely executed
        mctp_pkt_rx_thread.join()
        # wait until mctp_pkt_tx is completely executed
        mctp_pkt_tx_thread.join()

        log.info("MCTP PKT TX/RX Threads completely executed...")

    except Exception as e:
        log.exception("MCTP Transport Application bailed out due to , error:{}".format(e))

    sys.exit(0)

#Entry Point
if __name__ == '__main__':
    main()
