#!/bin/bash

FUN_ROOT="/opt/fungible"
DIR_FUN_CONFIG="/var/opt/fungible/fs1600/configure_bond"

if [[ "$EUID" -ne 0 ]]; then
        printf "Please run as ROOT EUID=$EUID\n"
        exit
fi

echo "Running $0 (`date`)"

SSHPASS=`which sshpass`
if [[ -z $SSHPASS ]]; then
	apt-get install -y sshpass
fi

IPMITOOL=`which ipmitool`
if [[ -z $IPMITOOL ]]; then
	apt-get install -y ipmitool
fi

BIN_TFTPD_HPA="/usr/sbin/in.tftpd"
if [[ ! -f $BIN_TFTPD_HPA ]]; then
	apt-get install -y tftpd-hpa
fi

if [[ -f $BIN_TFTPD_HPA ]]; then
	# Restrict the tftpserver to serve
	# requests only on the internal interface
	TFTP_SERVER_CONFIG_FILE="/etc/default/tftpd-hpa"
	grep "192" $TFTP_SERVER_CONFIG_FILE > /dev/null 2>&1
	RC=$?
	if [[ $RC -ne 0 ]]; then
		/bin/sed -i 's/TFTP_ADDRESS="/TFTP_ADDRESS="192.168.127.4/g' $TFTP_SERVER_CONFIG_FILE
	fi
	grep "create" $TFTP_SERVER_CONFIG_FILE > /dev/null 2>&1
	RC=$?
	if [[ $RC -ne 0 ]]; then
		/bin/sed -i 's/secure/secure --create/g' $TFTP_SERVER_CONFIG_FILE
	fi

	chown tftp:tftp /var/lib/tftpboot
	/bin/sed -i '/---secure/ s?---secure?--secure?' $TFTP_SERVER_CONFIG_FILE
fi

BIN_NETWORKMANAGER_FILE="/usr/sbin/NetworkManager"
if [[ ! -f $BIN_NETWORKMANAGER_FILE ]]; then
	apt-get install -y network-manager
fi

FUN_NETPLAN_YAML="/etc/netplan/fungible-netcfg.yaml"
if [[ -f $BIN_NETWORKMANAGER_FILE ]] && [[ -f $FUN_NETPLAN_YAML ]]; then
	grep NetworkManager $FUN_NETPLAN_YAML > /dev/null
	RC=$?
	if [[ $RC -ne 0 ]]; then
		/bin/sed -i 's/networkd/NetworkManager/g' $FUN_NETPLAN_YAML
		netplan apply
	fi
fi

CONFIG_DHCLIENT="/etc/dhcp/dhclient.conf"
if [[ -f $BIN_NETWORKMANAGER_FILE ]] && [[ -f $CONFIG_DHCLIENT ]]; then
	grep bootfile-name $CONFIG_DHCLIENT > /dev/null
	RC=$?
	if [[ $RC -ne 0 ]]; then
		sed -i 's/ntp-servers;/ntp-servers, bootfile-name;/g' $CONFIG_DHCLIENT
		# Restart netplan so that a DHCP request is triggered
		netplan apply
	fi
fi

UPDATE_GRUB=0
GRUB_FILE="/etc/default/grub"
if [[ -f $GRUB_FILE ]]; then
        # Check if iommu is enabled
        grep "GRUB_CMDLINE_LINUX" $GRUB_FILE | grep "iommu" > /dev/null
        RC=$?

        if [[ $RC -ne 0 ]]; then
                echo "Upgrade grub config file to enable iommu"
                /bin/sed -i '/GRUB_CMDLINE_LINUX.*115200n8/ s?115200n8?115200n8 intel_iommu=on iommu=pt?' $GRUB_FILE
                grep "GRUB_CMDLINE_LINUX" $GRUB_FILE | grep "iommu" > /dev/null
                RC=$?
                if [[ $RC -eq 0 ]]; then
                        echo "iommu configured in grub"
                        UPDATE_GRUB=1
                fi
        fi

        # Check if fsck is enabled
        grep "GRUB_CMDLINE_LINUX" $GRUB_FILE | grep "iommu" | grep "fsck" > /dev/null
        RC=$?

        if [[ $RC -ne 0 ]]; then
                echo "Upgrade grub config file to enable fsck upon every COMe boot-up"
                /bin/sed -i '/GRUB_CMDLINE_LINUX.*iommu=pt/ s?iommu=pt?iommu=pt fsck\.repair=yes fsck\.mode=force?' $GRUB_FILE
                grep "GRUB_CMDLINE_LINUX" $GRUB_FILE | grep "iommu" | grep "fsck" > /dev/null
                RC=$?
                if [[ $RC -eq 0 ]]; then
                        echo "fsck configured in grub"
                        UPDATE_GRUB=1
                fi
        fi

        # Check if debug is enabled
        grep "GRUB_CMDLINE_LINUX" $GRUB_FILE | grep "iommu" | grep "fsck" | grep "debug" > /dev/null
        RC=$?

        if [[ $RC -ne 0 ]]; then
                echo "Upgrade grub config file to enable debug upon every COMe boot-up"
                /bin/sed -i '/GRUB_CMDLINE_LINUX.*console=tty0/ s?console=tty0?debug console=tty0?' $GRUB_FILE
                grep "GRUB_CMDLINE_LINUX" $GRUB_FILE | grep "iommu" | grep "fsck" | grep "debug" > /dev/null
                RC=$?
                if [[ $RC -eq 0 ]]; then
                        echo "debug configured in grub"
                        UPDATE_GRUB=1
                fi
        fi

        # *** THIS IS A CRITICAL WINDOW ***
        if [[ $UPDATE_GRUB -eq 1 ]]; then
                update-grub
                sync
        fi
fi

function Is_Interface_Created()
{
        INTF=$1
        COUNT=30
        while [[ $COUNT -ne 0 ]]; do
                if [[ -d $INTF ]]; then
                        echo "Interface ($INTF) is created"
                        return 0;
                fi

                COUNT=$((COUNT - 1))
                sleep 1
        done

        echo "Interface ($INTF) is NOT created"

        return 1
}

function Is_Interface_Up()
{
        INTF=$1
        COUNT=10
        while [[ $COUNT -ne 0 ]]; do
                if [[ -f $INTF/operstate ]]; then
                        INTF_OPER_ST=`cat $INTF/operstate`
                        if [[ $INTF_OPER_ST == "up" ]]; then
                                echo "Interface ($INTF) is up"
                                return 0;
                        fi
                fi

                COUNT=$((COUNT - 1))
                sleep 1
        done

        echo "Interface ($INTF) is down"

        return 1
}

# Systemd starts the below 2 services simulataneously
# NetworkManager.service
# init-fs1600.service
# We have seen inconsistencies with NetworkManager
# bringing up interfaces and hence the blow checks

# Verify that the interface is created & operational
INTERNAL_VLAN_VIRT_INTF="/sys/class/net/enp3s0f0.2"

Is_Interface_Created $INTERNAL_VLAN_VIRT_INTF

# SWSYS-604 SWSYS-740
Is_Interface_Up $INTERNAL_VLAN_VIRT_INTF
RC=$?
if [[ $RC -ne 0 ]]; then
	echo "Retry to bring up $INTERNAL_VLAN_VIRT_INTF"
	netplan apply
	# check once more
	Is_Interface_Up $INTERNAL_VLAN_VIRT_INTF
fi

function Check_TftpdHpa()
{
	# Check if the tftpd-hpa server has started
	TFTPD_HPA_STATUS=`systemctl is-failed tftpd-hpa`
	echo "tftpd-hpa status: ${TFTPD_HPA_STATUS}"
	COUNT=30
	while [[ $COUNT -ne 0 ]]; do
		if [ ${TFTPD_HPA_STATUS} == "inactive" ]; then
			COUNT=$((COUNT - 1))
			sleep 1
		else
			break
		fi
	done
	TFTPD_HPA_STATUS=`systemctl is-failed tftpd-hpa`
	echo "tftpd-hpa status: ${TFTPD_HPA_STATUS}"
	# If the tftpd-hpa server is in failed state then restart
	if [ ${TFTPD_HPA_STATUS} == "failed" ]; then
		echo "Restarting tftpd-hpa server"
		systemctl restart tftpd-hpa
		TFTPD_HPA_STATUS=`systemctl is-failed tftpd-hpa`
		echo "tftpd-hpa status: ${TFTPD_HPA_STATUS}"
	fi
}

# SWSYS-741
/lib/systemd/systemd-sysv-install is-enabled tftpd-hpa
RC=$?
if [ ${RC} -eq 0 ]; then
	echo "tftpd-hpa server is enabled"
	Check_TftpdHpa
else
	echo "tftpd-hpa server is disabled"
fi

TFTPBOOT_DIR=/var/lib/tftpboot
if [[ -d $TFTPBOOT_DIR ]]; then
	HBM_SHARD_PREFIX=hbmdump_
	# Look for only the HBM shard files
	FILES=`ls $TFTPBOOT_DIR/hbmdump_* 2>/dev/null`
	if [[ ! -z "$FILES" ]]; then
		UPTIME=`cut -f1 -d. /proc/uptime`
		UPTIME_EPOCH=`date --utc -d "$UPTIME seconds ago" +"%s"`
		echo "COMe UPTIME since epoch $UPTIME_EPOCH"
		for F in $FILES; do
			# Time of last access of the file
			FILE_LAST_ACCESS_TIME=`stat -c %x $F`
			FILE_LAST_ACCESS_TIME_EPOCH=`date --utc -d "$FILE_LAST_ACCESS_TIME" +"%s"`
			if [[ "$UPTIME_EPOCH" > "$FTIME" ]]; then
				echo "Deleting file $F last accessed time since epoch $FILE_LAST_ACCESS_TIME_EPOCH"
				rm -f "$F"
			fi
		done

		sync
	fi
fi

IPMI_LAN="ipmitool -U admin -P admin lan print 1"
AWK_LAN='/IP Address[ ]+:/ {print $4}'
REBOOT_FILE="/tmp/host_reboot"

BMC_IP=$($IPMI_LAN | awk "$AWK_LAN")
printf "BMC eth0 IP: %s\n" $BMC_IP

if [[ -d /sys/class/net/enp3s0f0.2 ]]; then
	BMC_IP="192.168.127.2"
fi

printf "Poll BMC:  %s\n" $BMC_IP

BMC="-P password: -p superuser ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no sysadmin@$BMC_IP"

REBOOT=$(sshpass $BMC "ls $REBOOT_FILE" > /dev/null 2>&1)
if [ "$REBOOT" = "$REBOOT_FILE" ]; then
    printf "WARNING: BMC request to reboot host\n"
    sshpass $BMC "rm $REBOOT_FILE"
    reboot
else
	echo "Reboot from BMC not required. Continuing..."
fi

echo "Init CoSt Plane!!!"

# Hot-plug not supported so no need to wait if F1 are not see upon boot-up
BDFID=`lspci -d 1dad: | grep "Ethernet controller" | cut -d " " -f 1`
if [[ -z "$BDFID" ]]; then
	echo "F1 EP not found"
	exit 1
fi

# Find out how many F1's are available log for debugging
F1COUNT=`lspci -d 1dad: | grep "Ethernet controller" | cut -d " " -f 1 | wc -l`
echo "$F1COUNT F1 found"

export USER="fun"
export HOME="/home/fun"

mkdir -p $DIR_FUN_CONFIG
if [[ -f $DIR_FUN_CONFIG/configure_bond ]]; then
	$FUN_ROOT/cclinux/cclinux_service.sh --start --ep --storage --autocreatebond
else
	$FUN_ROOT/cclinux/cclinux_service.sh --start --ep --storage
fi

if [[ -f /var/log/old_hbm_dump ]] && [[ -f $FUN_ROOT/etc/DpuHealthMonitor.sh ]]; then
	$FUN_ROOT/etc/DpuHealthMonitor.sh &
else
	if [[ -f $FUN_ROOT/etc/DpuHealthMonitorNew.sh ]]; then
		$FUN_ROOT/etc/DpuHealthMonitorNew.sh &
	fi
fi

#Running DPCSH in TCP-PROXY Mode,
#so that BMC can use this interface
#to fetch F1s' data over NVME interfaces
BMC_F1_0_DPC_PORT=43101
BMC_F1_1_DPC_PORT=43102
BMC_DPCSH_F1_0_LOGF="/var/log/bmc_dpcsh_f1_0.log"
BMC_DPCSH_F1_1_LOGF="/var/log/bmc_dpcsh_f1_1.log"

BMC_F1_0_DPC_PORT2=43103
BMC_F1_1_DPC_PORT2=43104
BMC_DPCSH_F1_0_LOGF2="/var/log/bmc_dpcsh_f1_0_inst2.log"
BMC_DPCSH_F1_1_LOGF2="/var/log/bmc_dpcsh_f1_1_inst2.log"

F1_0_NVME="/dev/nvme0"
F1_1_NVME="/dev/nvme1"

# 10 seconds SWSYS-465
DPCSH_TIMEOUT="10000"

if [[ -f $FUN_ROOT/FunSDK/bin/Linux/dpcsh && -c $F1_0_NVME && -c $F1_1_NVME ]]; then
	$FUN_ROOT/FunSDK/bin/Linux/dpcsh --pcie_nvme_sock=$F1_0_NVME --nvme_cmd_timeout=$DPCSH_TIMEOUT --tcp_proxy=$BMC_F1_0_DPC_PORT > $BMC_DPCSH_F1_0_LOGF 2>&1 &
	$FUN_ROOT/FunSDK/bin/Linux/dpcsh --pcie_nvme_sock=$F1_1_NVME --nvme_cmd_timeout=$DPCSH_TIMEOUT --tcp_proxy=$BMC_F1_1_DPC_PORT > $BMC_DPCSH_F1_1_LOGF 2>&1 &

	# SWTOOLS-1540
	$FUN_ROOT/FunSDK/bin/Linux/dpcsh --pcie_nvme_sock=$F1_0_NVME --nvme_cmd_timeout=$DPCSH_TIMEOUT --tcp_proxy=$BMC_F1_0_DPC_PORT2 > $BMC_DPCSH_F1_0_LOGF2 2>&1 &
	$FUN_ROOT/FunSDK/bin/Linux/dpcsh --pcie_nvme_sock=$F1_1_NVME --nvme_cmd_timeout=$DPCSH_TIMEOUT --tcp_proxy=$BMC_F1_1_DPC_PORT2 > $BMC_DPCSH_F1_1_LOGF2 2>&1 &
fi
# Configure the management stack on the F1s
[ -f $FUN_ROOT/etc/come_config_mgmt.sh ] && $FUN_ROOT/etc/come_config_mgmt.sh

echo "$0 DONE!!! (`date`)"
