#!/usr/bin/python -u

import sys
import os
import time
import subprocess
import tempfile
import optparse
import signal

SB_01 = { "uart": "/dev/ttyUSB4",
          "baud": "1000000",
          "serverip": "172.17.1.1",
          "boardip": "172.17.1.2",
          "iface": "enp1s0f1",
          "chip": "f1" }

SB_02 = { "uart": "/dev/ttyUSB0",
          "baud": "1000000",
          "serverip": "172.16.1.1",
          "boardip": "172.16.1.2",
          "iface": "enp1s0f0",
          "chip": "f1" }

boards = {"sb-01": SB_01,
          "sb-02": SB_02 }

SCRIPT_HDR = """
  verbose on
  print Prodding u-boot
  send ""
  sleep 1
  send ""
  print "Waiting for u-boot..."
"""

SCRIPT_UBOOT = """
  expect {{
    "{uboot_prompt}"
    "Autoboot" send "noboot"
    timeout 20 exit
  }}

  send "loadx"
  ! sx -k {chain_uboot}
  print "Download complete, auth & boot"
  sleep 1
  send "auth; bootelf_u -p"
"""

SCRIPT_FUNOS_UART = """
# now wait for new u-boot
  expect {{
    "{uboot_prompt}"
    "Autoboot" send "noboot"
    timeout 20 goto no_uboot
  }}

  sleep 1
  timeout {global_timeout}
  send "loadx"
  ! sx -k {funos}

  print "Download complete, unzip time"
  sleep 2
  send ""
  send "setenv bootargs {bootargs}"
  sleep 1
  send "unzip 0xFFFFFFFF91000000 0xa800000020000000 ; {auth_boot_cmd}"

  expect {{
      "platform_halt:"
      ">>>>>> bug_check on vp 0x" goto funos_crashing
      timeout {exit_timeout} goto halt_timeout
  }}

funos_halted
  sleep 1
  print "FunOS halted OK, exiting"
  goto out

funos_crashing:
  expect {{
      "platform_halt:" goto funos_halted
      timeout 20 break
  }}
  print "FunOS crashed, but didn't see platform_halt"

halt_timeout:
  print "Timeout waiting for FunOS to platform halt"
  goto out

no_uboot:
  print "U-boot did not respond on UART. Exiting for restart."
  ! touch restart.fail
  goto out

out:
  sleep 1
  print "boot.script: killing minicom"
  ! cat {minicom_pid} | xargs kill -HUP
"""

SCRIPT_FUNOS_TFTP = """

# TFTP BOOT FTW
  print "boot.script: Waiting for u-boot"

# now wait for new u-boot
  expect {{
    "{uboot_prompt}"
    "Autoboot" send "noboot"
    timeout 20 goto no_uboot
  }}
  send ""
  timeout {global_timeout}

  print "\\nboot.script: bringing up the network"
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
  send "setenv serverip {serverip}"
  send "echo serverip_done"
  print ""
  expect {{
     "serverip_done"  break
     timeout 30 goto eep3
  }}

  send "setenv ipaddr {boardip}"
  send "echo ipaddr_done"
  print ""
  expect {{
     "ipaddr_done"   break
     timeout 30 goto eep3
  }}

  print "\\nChecking link status..."
  ! cat {minicom_pid} | xargs /home/cgray/bin/check-i40e-link.py {iface} restart.fail
  print "\\nLink status checked"

  print "\\n"
  send ""
  send "setenv bootargs {bootargs}"
  send ""

  print "\\n"
  print "boot.script: tftpftw"
  print "\\n"
  send "tftpboot 0xffffffff91000000 {serverip}:{funos} ; unzip 0xFFFFFFFF91000000 0xa800000020000000 ; {auth_boot_cmd}"
  print "\\n"

  expect {{
      "Starting application at" break
      timeout 30 goto eep3
  }}

  print "boot.script: waiting for FunOS to platform halt now"

  # if we see FunOS, expect bootstrap
  #expect {{
  #    "Welcome to FunOS" break
  #    timeout 10 goto halt_wait
  #}}

  expect {{
      "sending bootstrap WU" break
      timeout 10 goto no_boot
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
  print "boot.script: Timeout waiting for FunOS to platform halt"
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
  ! touch restart.fail
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

MAX_TIMEOUT = 45

def get_file_mime_info(filename):
    """returns mime-type for the provided file"""

    cmd = ['file',
           '-z', # assume compressed
           '--mime-type', # get mime-type string
           '-b', # brief output
           filename]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        sys.stderr.write('Error: Failed to read file details %d %s\n' %
                            (e.returncode, e.output))
        return ''
    return out.strip()

def assert_file_is_signed(filename):
    filetype = get_file_mime_info(filename)
    if filetype == 'application/x-executable':
        raise Exception("File is not signed")
    elif filetype == 'application/octet-stream':
        return


def do_sleep(secs):
    secs = float(secs)
    delta = 0.3
    waited = 0.0

    while (waited < secs):
        time.sleep(delta)
        waited += delta


def sighup_handler(signal, frame):
    # this method defines the handler i.e. what to do
    # when you receive a SIGHUP
    print("%s:SIGHUP received" % sys.argv[0])

def maybe_reset_target(options):
    if (options.reset):
        print("Resetting %s" % options.board)
        r = os.system("~cgray/bin/sb-jtag-reset.py %s" % options.board)

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
parser.add_option("-r", "--reset", action="store_true", default=False)
parser.add_option("-m", "--make-dir", action="store_true", default=False)
parser.add_option("-T", "--no-terminal-reset", action="store_true", default=False)
parser.add_option("-G", "--do-pgid", action="store_true", default=False)
parser.add_option("-t", "--timeout", action="store", type="int", default=5)
parser.add_option("-x", "--no-bootscript", action="store_true", default=False)
parser.add_option("-u", "--uboot", action="store", default=None)
parser.add_option("-N", "--no-boot", action="store_true", default=False)
parser.add_option("-P", "--postscript", action="store", default=None)
parser.add_option("-F", "--tftp", action="store_true", default=False)
parser.add_option("-b", "--board", action="store", default=None)
parser.add_option("--bootscript-only", action="store_true", help="Generate bootscript and terminate")

(options, args) = parser.parse_args()

if (options.board not in boards):
    print("must specify a board")
    sys.exit(1)

if (options.make_dir):
    path = tempfile.mkdtemp(dir=os.getcwd())
else:
    path = "."

global_timeout = None

if (options.no_boot):
    maybe_reset_target(options)
else:
    if len(args) < 1:
        parser.error("wrong number of arguments")
        sys.exit(1)

    krn = args[0]
    arg = " ".join(args[1:])
    board = boards[options.board]

    # arg fixups
    arg = arg.replace("--test-exit-fast", "")
    # arg += " --skip-mem-zero"

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
    exit_name = "%s/exitlog" % path
    pid_name = "%s/minicom.pid" % path
    dun_name = "%s/job.done" % path

    if options.uboot:
        assert_file_is_signed(options.uboot)

    assert_file_is_signed(krn)

    d = {} # options directory for the bootscript

    filetype = get_file_mime_info(krn)
    # we've already checked that it is not an executable file so this
    # if below is obsolete, but currently left for reference ... to be removed
    # in the future
    if filetype == 'application/x-executable':
        d['auth_boot_cmd'] = 'bootelf -p 0xa800000020000000'
    elif filetype == 'application/octet-stream':
        d['auth_boot_cmd'] = 'auth 0xa800000020000000; bootelf -p ${loadaddr}'

    d['bootargs'] = arg
    d['minicom_pid'] = pid_name
    d['uboot_prompt'] = "{} #".format(board['chip'])

    script = SCRIPT_HDR
    if not options.tftp:
        if options.uboot:
            d['chain_uboot'] = options.uboot

        # 15 mins max download + other timeout
        global_timeout = 900 + options.timeout * 60
        exit_timeout = options.timeout * 60

        d['funos'] = krn
        d['global_timeout'] = global_timeout
        d['exit_timeout'] = exit_timeout
    else:
        # maybe install the files
        d['funos'] = maybe_install_funos(krn)

        # make a timeout
        timeout = options.timeout
        if (timeout > MAX_TIMEOUT):
            timeout = MAX_TIMEOUT

        exit_timeout = timeout * 60
        global_timeout = 120 + exit_timeout

        d['global_timeout'] = global_timeout
        d['exit_timeout'] = exit_timeout

        d['serverip'] = board['serverip']
        d['boardip'] = board['boardip']
        d['iface'] = board['iface']

        if board.get("chain_uboot"):
            d['chain_uboot'] = board["chain_uboot"]

        if options.uboot:
            d['chain_uboot'] = options.uboot

    if d.get("chain_uboot"):
        script += SCRIPT_UBOOT

    if options.tftp:
        script += SCRIPT_FUNOS_TFTP
    else:
        script += SCRIPT_FUNOS_UART

    if not options.no_bootscript or options.bootscript_only:
        fl = open(script_name, "w")
        fl.write(script.format(**d))
        fl.close()

    if options.bootscript_only:
        print("Done generating bootscript, saving to {}".format(script_name))
        exit(0)

    # make our own process group for easier clean-up
    print("Making our own process group")
    if (options.do_pgid):
        os.setpgid(0,0)
    gpid = os.getpgrp()
    print("pgid now %s" % gpid)

    device = boards[options.board]["uart"]
    baud = boards[options.board]["baud"]
    os.system("echo '\nStarting job on board %s' >> %s" % (options.board, log_name))
    cmd = "/usr/bin/minicom -D %s -b %s -S %s -w -C %s" % (device, baud, script_name, log_name)

    # fork minicom to get its pid for later
    print("Forking minicom...")
    p = subprocess.Popen(cmd.split())

    fl = open(pid_name, "w")
    fl.write("%s" % p.pid)
    fl.close()

    # wait for minicom to exit/die or someone to want it dead
    t0 = time.time()
    do_kill = False
    while (p.returncode is None):
        do_sleep(1)
        p.poll()

        if (global_timeout is not None):
            if ((time.time() - t0) > global_timeout):
                print("global timeout reached")
                os.system("echo 'run_job: global timeout reached' >> %s" % (exit_name))
                do_kill = True

        if (os.path.exists(dun_name)):
            print("someone requested a kill, killing minicom")
            os.system("echo 'run_job: kill requested' >> %s" % (exit_name))
            do_kill = True

        # double check for platform_halt because runscript is terrible
        out = subprocess.Popen(['tail', '-3', log_name],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
        stdout,stderr = out.communicate()
        if "platform_halt" in stdout:
            print("platform halt detected, killing minicom")
            os.system("echo 'run_job: platform halt detected' >> %s" % (exit_name))
            do_kill = True

        if (do_kill):
            killcmd = "kill -HUP %s" % p.pid
            print("killing with '%s'" % killcmd)
            os.system(killcmd)
            print("waiting for its demise")
            p.wait()
            break

    if (p.returncode is not None):
        print("run_job: minicom exited")
        cmd = "echo 'run_job: minicom died of natural causes (%s)' >> %s" % (p.returncode, exit_name)
        print(cmd)
        os.system(cmd)
    else:
        print("run_job: we killed minicom")
        cmd = "echo 'run_job: minicom died of unnatural causes (%s)' >> %s" % (p.returncode, exit_name)
        print(cmd)
        os.system(cmd)

    #for i in range(30):
    #    print "run_job: pause"
    #    do_sleep(1)

    print("Minicom is dead. long live minicom, but fixing its terminal settings...")
    do_sleep(2)
    if (not options.no_terminal_reset):
        os.system("reset")
    print("log file at %s.txt" % log_name)
    os.system("cat %s | grep -v 'Xmodem sectors' > %s.txt" % (log_name, log_name))
    os.system("cat %s >> %s.txt" % (exit_name, log_name))
    os.system("echo 'Job completed on board %s' >> %s.txt" % (options.board, log_name))
    os.system("cat %s.txt | tail -20" % log_name)

    print("Cleaning my own process group")
    # make sure we catch the signal so we exit OK
    signal.signal(signal.SIGHUP, sighup_handler)
    killcmd = "kill -HUP -%s" % gpid
    print("killing with '%s'" % killcmd)
    try:
        os.system(killcmd)
    except:
        print("got signal in kill")
    print("run_job exiting")

    do_sleep(2)

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

