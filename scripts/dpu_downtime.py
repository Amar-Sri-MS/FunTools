#!/usr/bin/env python3
import paramiko
import socket
import time
import scapy.all as scapy
from scp import SCPClient
import argparse


src = 12345
dst = 12346
dip = "100.3.27.17"
sip = "100.3.27.18"
dmac = "00:23:45:67:89:ab"
smac = "54:11:11:11:0a:02"


srv = {"name":"fc50-327-cc", "user":"root", "pass":'',"intf":"fpg4"}
cli = {"name":"cab06-100g-2", "user":"root", "pass":'Precious1*',"intf":"et-0/0/24:1"}
in_pcap = "/tmp/in.pcap"
out_pcap="/tmp/out.pcap"
#packet tx rate in pps
R = 200
#test time interval
T = 1

def print_stdout(cmd,stdout):
    print(cmd)
    for line in stdout.read().splitlines():
        print(line)

def init(host):
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #host=socket.gethostbyname(srv["dpu"])
        #print(host)
        ret = ssh.connect(host["name"], username=host["user"], password=host["pass"])
        print("connected {}".format(host["name"]))
        return ssh
def get_dst_info(rx):
        cmd = "ifconfig " + srv["intf"]
        stdin, stdout, stderr = rx.exec_command(cmd, get_pty=True)
        for lines in stdout.read().splitlines():
            if "HWaddr" in lines.decode("ascii"):
                dmac = lines.decode('ascii').split()[-1]
            if "inet addr" in lines.decode("ascii"):
                for data in lines.decode('ascii').split():
                    if "addr" in data:
                        dip = data.split(":")[1]
def get_src_info(tx):
        cmd = "ifconfig " + cli["intf"]
        stdin, stdout, stderr = tx.exec_command(cmd, get_pty=True)
        for lines in stdout.read().splitlines():
            if "curr media" in lines.decode("ascii"):
                dmac = lines.decode('ascii').split()[-1]
            if "inet" in lines.decode("ascii"):
                for data in lines.decode('ascii').split():
                    if "local" in data:
                        dip = data.split("=")[1]
        

def prepare_pcap():
    pkt = scapy.Ether(dst=dmac,src=smac)/scapy.IP(src=sip,dst=dip)/scapy.TCP(sport=src,dport=dst)
    scapy.wrpcap(in_pcap, pkt)


def main():
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('--srv_hostname',type=str, default="", help="packet generator host name")
        arg_parser.add_argument('--srv_user', type=str, default="",help="packet generator login username")
        arg_parser.add_argument('--srv_password', type=str, default="",help="packet generator login password")
        arg_parser.add_argument('--srv_intf', type=str, default="",help="packet generator interface to pump traffic")
        arg_parser.add_argument('--cli_hostname', type=str, default="",help="DPU host name")
        arg_parser.add_argument('--cli_user', type=str, default="",help="DPU login username")
        arg_parser.add_argument('--cli_password', type=str, default="",help="DPU login password")
        arg_parser.add_argument('--cli_intf', type=str, default="",help="DPU interface to pump traffic")
        arg_parser.add_argument('--time', type=int, default=10,help="time(secs) to run traffic")
        arg_parser.add_argument('--pps', type=int, default=100,help="rate(pps) of traffic")
        args = arg_parser.parse_args()

        if(args.srv_hostname != ""):
            srv["name"]=args.srv_hostname
        if(args.srv_user != ""):
            srv["name"]=args.srv_user
        if(args.srv_password != ""):
            srv["name"]=args.srv_password
        if(args.srv_intf != ""):
            srv["name"]=args.srv_intf

        if(args.cli_hostname != ""):
            cli["name"]=args.cli_hostname
        if(args.cli_user != ""):
            cli["name"]=args.cli_user
        if(args.cli_password != ""):
            cli["name"]=args.cli_password
        if(args.cli_intf != ""):
            cli["name"]=args.cli_intf

        T = args.time
        R = args.pps

        print("srv {}".format(srv))
        print("cli {}".format(cli))

        rx = init(srv)
        tx = init(cli)

        get_dst_info(rx)
        get_src_info(tx)
        print("src mac={} ip={} port={}".format(smac, sip, src))
        print("dst mac={} ip={} port={}".format(dmac, dip, dst))

        #TODO check conn between srv and cli
        '''
        cmd = "ping -c 1 "+ "1.1.1.1"
        stdin, stdout, stderr = tx.exec_command(cmd, get_pty=True)
        print("rx {} <===> tx {}".format(dip,sip))
        output = stderr.read().splitlines()
        print(stderr.channel.recv_exit_status())
        print (stdout.channel.recv_exit_status())
        if output.decode('ascii') != '0':
            print("no connection!!")
            return
        else:
            print("OK!")
        '''
        '''
        # prepare DPU
        # generate the pcap 
        # scp pcap to qfx
        # capture packets
        # send pkts
        # get stats
        # tear down
        '''
        #prepare DPU
        cmd = 'pgrep health'
        stdin, stdout, stderr = rx.exec_command(cmd, get_pty=True)
        pid_list = stdout.read().decode('ascii').splitlines()
        cmd = "kill -9 "
        for pid in pid_list:
            cmd += " " + pid
        print(cmd)
        stdin, stdout, stderr = rx.exec_command(cmd, get_pty=True)

        # generate the pcap 
        prepare_pcap()

        # copy pcap 
        ftp_client=SCPClient(tx.get_transport(), socket_timeout=15.0)
        ftp_client.put(in_pcap, in_pcap)
        ftp_client.close()

        # run tcpdump
        cmd = "nohup tcpdump -n -U -i "+cli["intf"]+" -w "+out_pcap+" port "+ str(dst)+" & \n"
        stdin, stdout, stderr = tx.exec_command(cmd, get_pty=True)
        pid = stdout.read().decode('ascii').splitlines()[0].split(" ")[1]
        print(cmd)

        # run tcpreplay
        output = ""
        count = T * R
        cmd = "/opt/sbin/tcpreplay -q -K -l "+str(count)+" -p "+str(R)+" -i "+cli["intf"]+ " "+in_pcap
        print(cmd)
        stdin, stdout, stderr = tx.exec_command(cmd, get_pty=True)
        #get the actual PPS
        output = stdout.read().splitlines()
        for line in output:
            if "Rated" in line.decode('ascii'):
                # format = Rated: x bps, y Mbps/sec, z pps
                r = line.decode('ascii').split(", ")[-1].split(" ")[0]
                r = float(r)
                break
        #print( "PPS = {}".format(r) )
        
        time.sleep(1)

        #get stats
        cmd = "tcpdump -n -U -r "+out_pcap+" | grep Out | wc -l"
        stdin, stdout, stderr = tx.exec_command(cmd, get_pty=True)
        sent = stdout.read().splitlines()[-1].decode('ascii')
        #print(sent)
        sent = float(sent)
        #print("tx pkts = {}".format(sent))
        cmd = "tcpdump -n -U  -r "+out_pcap+" | grep In | wc -l"
        stdin, stdout, stderr = tx.exec_command(cmd, get_pty=True)
        receive = stdout.read().splitlines()[-1].decode('ascii')
        #print(receive)
        receive = float(receive)
        #print("rx pkts = {}".format(receive))

        #print stats
        print ("configured values: rate = {} tx pkts={}".format(R, count))
        print ("actual values: rate = {} tx pkts={} rx pkts={}".format(r, sent, receive))
        print("downtime = {:.6f} ms".format((count - receive)*1000/ r))
        print("extratime = {:.6f} ms".format((sent - receive)*1000/ r))

        #TODO cleanup
        cmd = "kill -9  " + pid
        stdin, stdout, stderr = tx.exec_command(cmd.encode("ascii"), get_pty=True)
        print(cmd)
        cmd = "rm "+out_pcap + " "+in_pcap
        stdin, stdout, stderr = tx.exec_command(cmd.encode("ascii"), get_pty=True)
        print(cmd)


if __name__ == "__main__":
    main()
