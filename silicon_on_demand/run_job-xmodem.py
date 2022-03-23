#!/usr/bin/python -u

import sys
import os
import time
import subprocess
import tempfile
import optparse
import signal

SCRIPT_HDR = """
# blah
  print Prodding u-boot
  send ""
  sleep 1
  send ""
  sleep 1
  send ""
  print "Waiting for u-boot..."
"""

SCRIPT_UBOOT = """
  expect {
  	 "f1 #"
  	 timeout 20 exit
  }

  send "loadx"
  ! sx -k %s
  send "bootelf -p 0xFFFFFFFF91000000"
"""

SCRIPT_FUNOS = """
# now wait for new u-boot
  expect {
  	 "f1 #"
  	 timeout 20 goto no_uboot
  }

  timeout %s
  send "loadx"
  ! sx -k %s

  print "Download complete, unzip time"
  sleep 2
  send ""
  send ""
  send "unzip 0xFFFFFFFF91000000 0xFFFFFFFF99000000"

  # kick it again
  print "Unzip done, waiting for u-boot prompt"
  sleep 1
  send ""

  expect {
  	 "f1 #"
  	 timeout 20 goto no_unzip
  }

# save some command to nvram
  send "setenv bootargs %s"
  send "bootelf -p 0xFFFFFFFF99000000"

  expect {
      "platform_halt:"
      timeout %s goto halt_timeout
  }

  sleep 1
  print "FunOS halted OK, exiting"
  goto out

halt_timeout:
  print "Timeout waiting for FunOS to platform_halt"
  goto out

no_unzip:
  print "FunOS failed to unzip. Exiting"
  goto out

no_uboot:
  print "U-boot did not respond on UART. Exiting."
  goto out

out:
  sleep 1
  ! cat %s | xargs kill -HUP 
"""

SCRIPT_TFTP = """

# TFTP BOOT FTW
  print Waiting for u-boot
  send ""

# now wait for new u-boot
  expect {{
  	 "f1 #"
  	 timeout 20 goto no_uboot
  }}

  timeout {global_timeout}
  send "loadx"
  ! sx -k /home/mboksanyi/u-boot.mpg.gz

  print ""
  print ""
  print "boot.script: xmodem send done, chilling"
  sleep 5
  send ""
  send "unzip 0xFFFFFFFF91000000 0xFFFFFFFF99000000"

# save some command to nvram
  print "boot.script: Waiting for u-boot elf to unzip"
  send "echo unzip done"
  expect {{
  	 "unzip done"
  	 timeout 20 goto eep1
  }}

  send ""
  send "bootelf -p 0xFFFFFFFF99000000"

  print "boot.script: waiting to say hi"
  sleep 5
  send ""
  send "echo new uboot"
  print ""
  expect {{
  	 "new uboot"
  	 timeout 20 goto eep2
  }}

  print "boot.script: sending a bunch of commands"
  send "lfw"
  send "echo lfw_done"
  print ""
  expect {{
  	 "lfw_done"
  	 timeout 30 goto eep3
  }}
  
  send "lmpg"
  send "echo lmpg_done"
  print ""
  expect {{
  	 "lmpg_done"
  	 timeout 30 goto eep3
  }}
  
  send "ltrain"
  send "echo ltrain_done"
  print ""
  expect {{
  	 "ltrain_done"
  	 timeout 30 goto eep3
  }}
  
  send "lstatus"
  send "echo lstatus_done"
  print ""
  expect {{
  	 "lstatus_done"
  	 timeout 30 goto eep3
  }}
  
  print "boot.script: configuring IP"
  send "setenv serverip 172.16.1.1"
  send "echo serverip_done"
  print ""
  expect {{
  	 "serverip_done"  break
  	 timeout 30 goto eep3
  }}

  send "setenv ipaddr 172.16.1.2"
  send "echo ipaddr_done"
  print ""
  expect {{
  	 "ipaddr_done"   break
  	 timeout 30 goto eep3
  }}
  
  print "\\nChecking link status..."
  ! cat {minicom_pid} | xargs /home/cgray/bin/check-i40e-link.py enp1s0f0 restart.fail 
  print "\\nLink status checked"

  print "\\n"
  send ""
  send "setenv bootargs {bootargs}"
  send ""

  print "\\n"
  print "boot.script: tftpftw"
  print "\\n"
  send "tftpboot 0xffffffff91000000 172.16.1.1:{funos} ; unzip 0xFFFFFFFF91000000 0xFFFFFFFF99000000 ; bootelf -p 0xFFFFFFFF99000000"
  print "\\n"

  print "boot.script: waiting for FunOS to platform_halt now"

  # if we see FunOS, expect bootstrap
  expect {{
      "Welcome to FunOS" break
      timeout 10 goto halt_wait
  }}

  expect {{
      "sending bootstrap WU" break
      timeout 30 goto no_boot
  }}

halt_wait:
  expect {{
      "platform_halt:"
      timeout {exit_timeout} goto halt_timeout
  }}

  # now wait for the newline
  expect {{
      "\\n"
      timeout 2 break
  }}

  sleep 1
  print "\\nFunOS halted OK, exiting"
  goto out

halt_timeout:
  print "Timeout waiting for FunOS to platform_halt"
  goto out
no_uboot:
  print "boot.script: no uboot"
  print "\\n"
  goto out
eep1:
  print "boot.script: eep1"
  print "\\n"
  goto out
eep2:
  print "boot.script: eep2"
  print "\\n"
  goto out
eep3:
  print "boot.script: eep3"
  print "\\n"
  goto out
eep4:
  print "boot.script: eep4"
  print "\\n"
  goto out
no_boot:
  print "boot.script: FunOS hung booting. Timeout."
  print "\\n"
  goto out
out:
  print "boot.script: cleaning up"
  print "\\n"
  sleep 1
  ! cat {minicom_pid} | xargs kill -HUP
"""


def sighup_handler(signal, frame):
    # this method defines the handler i.e. what to do
    # when you receive a SIGHUP
    print("%s:SIGHUP received" % sys.argv[0])

def maybe_reset_target(options):
    tfile = options.reset_file
    if (tfile is not None):
        # XXX: assume file == reset probe
        print("Resetting sb-02")
        r = os.system("~cgray/bin/sb-jtag-reset.py sb-02")
        #if (r != 0):
        #    print "Probe reset returned an error. FAILING"
        #    sys.exit(1)
        print("Waiting for a reset")
        time.sleep(15)

def maybe_install_funos(funos):

    # OK if it's not absolute
    if (funos[0] != "/"):
        return funos

    uname = "dunno"
    os.system("mkdir -p /home/mboksanyi/tftpboot/%s" % uname)

    binname = os.path.split(funos)[-1]
    ofunos = funos
    funos = "%s/%s" % (uname, binname)

    os.system("cp %s /home/mboksanyi/tftpboot/%s" % (ofunos, funos))
    
    return funos

parser = optparse.OptionParser(usage="usage: %prog [options] funos-stripped.gz [-- bootargs]")
parser.add_option("-r", "--reset-file", action="store", default=None)
parser.add_option("-m", "--make-dir", action="store_true", default=False)
parser.add_option("-T", "--no-terminal-reset", action="store_true", default=False)
parser.add_option("-G", "--do-pgid", action="store_true", default=False)
parser.add_option("-t", "--timeout", action="store", type="int", default=5)
parser.add_option("-x", "--no-bootscript", action="store_true", default=False)
parser.add_option("-u", "--uboot", action="store", default=None)
parser.add_option("-N", "--no-boot", action="store_true", default=False)
parser.add_option("-P", "--postscript", action="store", default=None)
parser.add_option("-F", "--tftp", action="store_true", default=False)

(options, args) = parser.parse_args()

if (options.make_dir):
    path = tempfile.mkdtemp(dir=os.getcwd())
else:
    path = "."
        
if (options.no_boot):
    maybe_reset_target(options)
else:
    if len(args) < 1:
        parser.error("wrong number of arguments")
        sys.exit(1)

    krn = args[0] 
    arg = " ".join(args[1:])

    # arg fixups
    arg = arg.replace("--test-exit-fast", "")
    arg += " --skip-mem-zero"
    
    maybe_reset_target(options)

    # make sure the kernel exists
    if (not options.tftp):
        if (not os.path.isfile(krn)):
            # clean exit so the server moves on
            print("FunOS binary doesn't exist: %s" % krn)
            sys.exit(0)

        if (os.path.getsize(krn) > (10*1024*1024)):
            # clean exit so the server moves on
            print("FunOS binary > 10MB. Is it compressed?")
            sys.exit(0)

    print("Putting output files in %s" % path)

    script_name = "%s/boot.script" % path
    log_name = "%s/minicom-log" % path
    pid_name = "%s/minicom.pid" % path
    dun_name = "%s/job.done" % path

    if (not options.tftp):
        script = SCRIPT_HDR
        if (options.uboot is not None):
            script += SCRIPT_UBOOT % options.uboot

        # 15 mins max download + other timeout
        global_timeout = 900 + options.timeout * 60
        exit_timeout = options.timeout * 60
        script += SCRIPT_FUNOS % (global_timeout, krn, arg, exit_timeout, pid_name)
    else:
        # maybe install the files
        krn = maybe_install_funos(krn)
        
        # make the args
        d = {}
        d['global_timeout'] = 120 + options.timeout * 60
        d['exit_timeout'] = options.timeout * 60
        d['bootargs'] = arg
        d['funos'] = krn
        d['minicom_pid'] = pid_name
        
        script = SCRIPT_TFTP.format(**d)
    
    if (not options.no_bootscript):
        fl = open(script_name, "w")
        fl.write(script)
        fl.close()

    # make our own process group for easier clean-up
    print("Making our own process group")
    if (options.do_pgid):
        os.setpgid(0,0)
    gpid = os.getpgrp()
    print("pgid now %s" % gpid)

    cmd = "minicom -D /dev/ttyUSB0 -S %s -w -C %s" % (script_name, log_name)

    # fork minicom to get its pid for later
    print("Forking minicom...")
    p = subprocess.Popen(cmd, shell=True)

    fl = open(pid_name, "w")
    fl.write("%s" % p.pid)
    fl.close()

    # wait for minicom to exit/die or someone to want it dead
    while (p.returncode is None):
        time.sleep(1)
        p.poll()
        if (os.path.exists(dun_name)):
            print("someone requested a kill, killing minicom")
            killcmd = "kill -HUP %s" % p.pid
            print("killing with '%s'" % killcmd)
            os.system(killcmd)
            print("waiting for its demise")
            p.wait()
            break


    print("Minicom is dead. long live minicom, but fixing its terminal settings...")
    time.sleep(2)
    if (not options.no_terminal_reset):
        os.system("reset")
    print("log file at %s.txt" % log_name)
    os.system("cat %s | grep -v 'Xmodem sectors' > %s.txt" % (log_name, log_name))
    os.system("cat %s.txt | tail -20" % log_name)

    print("Cleaning my own process group")
    # make sure we catch the signal so we exit OK
    signal.signal(signal.SIGHUP, sighup_handler)
    killcmd = "kill -HUP -%s" % gpid
    print("killing with '%s'" % killcmd)
    time.sleep(2)
    try:
        os.system(killcmd)
    except:
        print("got signal in kill")
    print("run_job exiting")

# if there's a restart fail, we don't want to run the postscript
job_ok = not os.path.exists("restart.fail")

# see if we need to post-jtag it
if (job_ok and (options.postscript is not None)):
    logname = "%s/postscript-log.txt" % path
    postscript = "%s 2>&1 | tee %s" % (options.postscript, logname)

    #if (not os.path.exists(options.postscript)):
    #    print "ERROR: cannot find file %s" % jpscript
    #    sys.exit(1)

    os.system(postscript)

    # now append it to the full log
    log2name = "%s/minicom-log.txt" % path
    os.system("cat %s >> %s" % (logname, log2name))
    

# exit cleanly
sys.exit(0)

