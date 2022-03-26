#!/usr/bin/python3

import argparse
import requests
import json

SI_AGENT_PORT = "5000"

# Mapping from FC200 to its cclinux IP address
FC_MAP = {
	"fc200-9": "10.1.107.191"
}

def send_rest_api(http_action, url, params={}, verbose=True):
    """Helper function to send REST API requests to storage agent"""
    resp = {}
    headers = {'content-type': 'application/json'}
    if verbose:
        print(http_action, url, params)

    if http_action == 'get':
        resp = requests.get(url, auth=('admin', 'password'),\
                headers=headers, json=params, verify=False)
    elif http_action == 'post':
        resp = requests.post(url, auth=('admin', 'password'),\
                headers=headers, json=params, verify=False)
    elif http_action == 'put':
        resp = requests.put(url, auth=('admin', 'password'),\
                headers=headers, json=params, verify=False)
    elif http_action == 'patch':
        resp = requests.patch(url, auth=('admin', 'password'),\
                headers=headers, json=params, verify=False)
    elif http_action == 'delete':
        resp = requests.delete(url, auth=('admin', 'password'),\
                headers=headers, json=params, verify=False)
    else:
        return resp

    return resp

def create_pci_ctrlr(ctrlr_uuid, subsys_nqn):
    """Helper function to create PCI controller on S1"""
    params = {
            'ctlid': 0,
            'ctrlr_id': 0,
            'ctrlr_type': "BLOCK",
            'uuid': ctrlr_uuid,
            'fnid': 3,
            'huid': 1,
            'subsys_nqn': subsys_nqn,
            'transport': "PCI"
    }
    url = "https://{}:{}/{}".format(FC_MAP['fc200-9'], SI_AGENT_PORT,
                                    "storage_agent/controller")
    send_rest_api('post', url, params)

def create_rds_vol(vol_size, host_ip, remote_ip, subsys_nqn, remote_nsid, vol_id, vol_uuid):
    """Helper function to create RDS volume on S1"""
    host_nqn = "nqn.2015-09.com.fungible:{}".format(host_ip)
    name = "rdsvol-{}".format(vol_id)
    params = {
            'block_size': 4096,
            'capacity': vol_size,
            'host_nqn': host_nqn,
            'name': name,
            'port': 4420,
            'remote_ip': remote_ip,
            'remote_nsid': remote_nsid,
            'subsys_nqn': subsys_nqn,
            'transport': 'TCP',
            'type': 'VOL_TYPE_BLK_RDS',
            'uuid': vol_uuid
    }
    url = "https://{}:{}/{}".format(FC_MAP['fc200-9'], SI_AGENT_PORT,
                                    "storage_agent/volumes")
    resp = send_rest_api('post', url, params)

def attach_rds_vol(ctrlr_uuid, nsid, vol_uuid):
    params = {
            'ana_state': 'optimized',
            'ctrlr_uuid': ctrlr_uuid,
            'enable_connection': True,
            'nsid': nsid,
            'vol_uuid': vol_uuid
    }
    url = "https://{}:{}/{}".format(FC_MAP['fc200-9'], SI_AGENT_PORT,
                                    "storage_agent/ports")
    send_rest_api('post', url, params)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    create_ctrlr_parser = subparsers.add_parser("create-ctrlr", help="Create a controller on SI")
    create_ctrlr_parser.add_argument('ctrlr_uuid', type=str, help="UUID of the controller on SI")
    create_ctrlr_parser.add_argument('subsys_nqn', type=str, help="Subsystem NQN")

    create_vol_parser = subparsers.add_parser("create-vol", help="Create a volume on SI")
    create_vol_parser.add_argument(dest='volsize', type=int, help="Volume size", nargs='?')
    create_vol_parser.add_argument(dest='host_ip', type=str, help='Host IP address', nargs='?')
    create_vol_parser.add_argument(dest='remote_ip', type=str, help='Remote IP address', nargs='?')
    create_vol_parser.add_argument('subsys_nqn', type=str, help="Subsystem NQN")
    create_vol_parser.add_argument(dest='remote_nsid', type=int, help='Namespace ID for the remote namespace', nargs='?')
    create_vol_parser.add_argument(dest='vol_id', type=int, help='Volume ID', nargs='?')
    create_vol_parser.add_argument(dest='vol_uuid', type=str, help='UUID of the volume', nargs='?')

    attach_parser = subparsers.add_parser("attach", help="Attach a volume")
    attach_parser.add_argument('ctrlr_uuid', type=str, help="UUID of the controller on SI")
    attach_parser.add_argument(dest='nsid', type=int, help='Namespace ID for the volume on SI', nargs='?')
    attach_parser.add_argument(dest='vol_uuid', type=str, help='UUID of the volume', nargs='?')

    args = parser.parse_args()
    if args.command == "create-ctrlr":
        print("create ctrlr")
        create_pci_ctrlr(args.ctrlr_uuid, args.subsys_nqn)
    elif args.command == "create-vol":
        print("create vol")
        create_rds_vol(args.volsize, args.host_ip, args.remote_ip,
                       args.subsys_nqn, args.remote_nsid, args.vol_id,
                       args.vol_uuid)
    elif args.command == "attach":
        print("attach")
        attach_rds_vol(args.ctrlr_uuid, args.nsid, args.vol_uuid)
