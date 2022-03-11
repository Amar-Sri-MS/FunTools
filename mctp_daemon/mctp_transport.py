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

SMBUS_TX_FIFO = '/tmp/mctp_smbus_tx'
SMBUS_RX_FIFO = '/tmp/mctp_smbus_rx'

#PLDM/MCTP Packet Egress Path
def mctp_pcievdm_pkt_tx():
    log.info("Started a thread to send PLDM/MCTP Pkts to HostServer ...")
    try:
        mctp_tx_dpc_handle = dpc_client.DpcClient(unix_sock = True)
        with open(PCIEVDM_TX_FIFO, 'rb') as pcievdm_tx_fifo:
            #Make Reader FD as NonBlocking
            os.set_blocking(pcievdm_tx_fifo.fileno(), False)
            log.info("PCIEVDM_TX_FIFO opened")
            while True:
                log.debug('Waiting for the PLDM/MCTP Over PCIeVDM Packets from MCTP Daemon.....')
                mctp_pcievdm_pkt_tx_data = pcievdm_tx_fifo.read()
                if mctp_pcievdm_pkt_tx_data is None or len(mctp_pcievdm_pkt_tx_data) == 0:
                    time.sleep(1)
                    continue

                log.debug('Read data from FIFO before Bin -> Blob conversion: %s', mctp_pcievdm_pkt_tx_data)
                data = mctp_tx_dpc_handle.blob_from_string(mctp_pcievdm_pkt_tx_data)

                log.debug('Sending Data to HostServer using FunOS PCIe Driver')
                result = mctp_tx_dpc_handle.execute('mctp_transport', ['mctp_pkt_send', 'mctp_over_pcievdm', ['quote', data]])
                log.debug("'mctp_pkt_send' packet DPCSH response: {}".format(result))

    except Exception as e:
        pcievdm_tx_fifo.close()
        result = mctp_tx_dpc_handle.execute("mctp_transport", ['mctp_pkt_recv_unsub', 0])
        log.exception(" mctp_pcievdm_pkt_tx() failed, error:{}".format(e))
  
def mctp_smbus_pkt_tx():
    log.info("Started a thread to send PLDM/MCTP Pkts to HostServer ...")
    try:
        mctp_tx_dpc_handle = dpc_client.DpcClient(unix_sock = True)
        with open(SMBUS_TX_FIFO, 'rb') as smbus_tx_fifo:
            #Make Reader FD as NonBlocking
            os.set_blocking(smbus_tx_fifo.fileno(), False)
            log.info("SMBUS_TX_FIFO opened")
            while True:
                log.debug('Waiting for the PLDM/MCTP Over SMBus Packets from MCTP Daemon.....')
                mctp_smbus_pkt_tx_data = smbus_tx_fifo.read()
                if mctp_smbus_pkt_tx_data is None or len(mctp_smbus_pkt_tx_data) == 0:
                    time.sleep(1)
                    continue

                log.debug('Read data from FIFO before Bin -> Blob conversion: %s', mctp_smbus_pkt_tx_data)
                data = mctp_tx_dpc_handle.blob_from_string(mctp_smbus_pkt_tx_data)

                log.debug('Sending Data to HostServer using FunOS PCIe Driver')
                result = mctp_tx_dpc_handle.execute('mctp_transport', ['mctp_pkt_send', 'mctp_over_smbus', ['quote', data]])
                log.debug("'mctp_pkt_send' packet DPCSH response: {}".format(result))

    except Exception as e:
        smbus_tx_fifo.close()
        result = mctp_tx_dpc_handle.execute("mctp_transport", ['mctp_pkt_recv_unsub', 1])
        log.exception(" mctp_smbus_pkt_tx() failed, error:{}".format(e))

#PLDM/MCTP Packet Ingress Path
def mctp_pcievdm_pkt_rx():
    log.info("Started a thread to receive PLDM/MCTP Pkts to HostServer ...")

    try:
        mctp_rx_dpc_handle = dpc_client.DpcClient(unix_sock = True)
        #Start a Fresh
        mctp_rx_dpc_handle.execute("mctp_transport", ['mctp_pkt_recv_unsub', 0])
        mctp_rx_dpc_handle.execute("mctp_transport", ['mctp_pkt_recv_unsub', 1])

        #Subscribe to a MCTP Transport Channel to RX Packets
        tid = mctp_rx_dpc_handle.async_send("mctp_transport", "mctp_pkt_recv_sub")

        result = mctp_rx_dpc_handle.async_recv_wait(tid)
        log.info("MCTP Rx Channel Successfully established: {}".format(result))

        with open(PCIEVDM_RX_FIFO, 'wb') as pcievdm_rx_fifo:
            log.info("PCIEVDM_RX_FIFO opened")
            while True:
                log.debug("Waiting for PLDM/MCTP Packet from Host Server ........")
                result = mctp_rx_dpc_handle.async_recv_wait(tid)
                log.debug("PLDM/MCTP async_recv_wait recieved response: {}".format(result))

                if not result['mctp_over_pcievdm']:
                    log.debug("pkt != PLDM/MCTP Over PCIeVDM")
                    continue

                mctp_pcievdm_pkt_rx_data = mctp_rx_dpc_handle.blob_to_string(result['data'])
                log.debug('Sending PLDM/MCTP Packet to MCTP Daemon for Processing: %s', mctp_pcievdm_pkt_rx_data)

                pcievdm_rx_fifo.write(mctp_pcievdm_pkt_rx_data)
                #Flush is mandatory for proper writing data to Daemon FIFO
                pcievdm_rx_fifo.flush()
                time.sleep(1)

    except Exception as e:
        pcievdm_rx_fifo.close()
        result = mctp_rx_dpc_handle.execute("mctp_transport", ['mctp_pkt_recv_unsub', 0])
        log.exception("mctp_pcievdm_pkt_rx() failed, error:{}".format(e))

def mctp_smbus_pkt_rx():
    log.info("Started a thread to receive PLDM/MCTP Pkts to HostServer ...")

    try:
        mctp_rx_dpc_handle = dpc_client.DpcClient(unix_sock = True)

        #Subscribe to a MCTP Transport Channel to RX Packets
        tid = mctp_rx_dpc_handle.async_send("mctp_transport", "mctp_pkt_recv_sub")

        result = mctp_rx_dpc_handle.async_recv_wait(tid)
        log.info("MCTP Rx Channel Successfully established: {}".format(result))

        with open(SMBUS_RX_FIFO, 'wb') as smbus_rx_fifo:
            log.info("SMBUS_RX_FIFO opened")
            while True:
                log.debug("Waiting for PLDM/MCTP Packet from Host Server ........")
                result = mctp_rx_dpc_handle.async_recv_wait(tid)
                log.debug("PLDM/MCTP async_recv_wait recieved response: {}".format(result))

                if not result['mctp_over_smbus']:
                    log.debug("pkt != PLDM/MCTP Over PCIeVDM")
                    continue

                mctp_smbus_pkt_rx_data = mctp_rx_dpc_handle.blob_to_string(result['data'])
                log.debug('Sending PLDM/MCTP Packet to MCTP Daemon for Processing: %s', mctp_smbus_pkt_rx_data)

                smbus_rx_fifo.write(mctp_smbus_pkt_rx_data)
                #Flush is mandatory for proper writing data to Daemon FIFO
                smbus_rx_fifo.flush()
                time.sleep(1)

    except Exception as e:
        smbus_rx_fifo.close()
        result = mctp_rx_dpc_handle.execute("mctp_transport", ['mctp_pkt_recv_unsub', 1])
        log.exception("mctp_smbus_pkt_rx() failed, error:{}".format(e))

# Main Function of MCTP Transport CCLinux GlueLayer
def main():

    try:
        log.info("Waiting for the MCTP Daemon to Start............")
        while True:
            if not os.path.exists(PCIEVDM_TX_FIFO) or not os.path.exists(PCIEVDM_RX_FIFO) or not stat.S_ISFIFO(os.stat(PCIEVDM_TX_FIFO).st_mode) or not stat.S_ISFIFO(os.stat(PCIEVDM_RX_FIFO).st_mode):
                continue
            elif not os.path.exists(SMBUS_TX_FIFO) or not os.path.exists(SMBUS_RX_FIFO) or not stat.S_ISFIFO(os.stat(SMBUS_TX_FIFO).st_mode) or not stat.S_ISFIFO(os.stat(SMBUS_RX_FIFO).st_mode):
                continue
            else:
                break

        log.info("Starting MCTP Transport CCLinux GlueLayer .....")
        # creating mctp_pcievdm_pkt_tx/rx threads
        mctp_pcievdm_pkt_rx_thread = threading.Thread(target=mctp_pcievdm_pkt_rx)
        mctp_pcievdm_pkt_tx_thread = threading.Thread(target=mctp_pcievdm_pkt_tx)
  
        # starting mctp_pcievdm_pkt_rx
        mctp_pcievdm_pkt_rx_thread.start()
        # starting mctp_pcievdm_pkt_tx
        mctp_pcievdm_pkt_tx_thread.start()
  
        # creating mctp_smbus_pkt_tx/rx threads
        mctp_smbus_pkt_rx_thread = threading.Thread(target=mctp_smbus_pkt_rx)
        mctp_smbus_pkt_tx_thread = threading.Thread(target=mctp_smbus_pkt_tx)

        # starting mctp_smbus_pkt_rx
        mctp_smbus_pkt_rx_thread.start()
        # starting mctp_smbus_pkt_tx
        mctp_smbus_pkt_tx_thread.start()

        # wait until mctp_pcievdm_pkt_rx is completely executed
        mctp_pcievdm_pkt_rx_thread.join()
        # wait until mctp_pcievdm_pkt_tx is completely executed
        mctp_pcievdm_pkt_tx_thread.join()

        # wait until mctp_smbus_pkt_rx is completely executed
        mctp_smbus_pkt_rx_thread.join()
        # wait until mctp_smbus_pkt_tx is completely executed
        mctp_smbus_pkt_tx_thread.join()

        log.info("MCTP PKT TX/RX Threads completely executed...")

    except Exception as e:
        log.exception("MCTP Transport Application bailed out due to , error:{}".format(e))

    sys.exit(0)

#Entry Point
if __name__ == '__main__':
    main()
