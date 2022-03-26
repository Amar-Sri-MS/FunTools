#!/usr/bin/python -u

import sys
import os
import stat
import optparse
import datetime
import tempfile
import subprocess
import json
import signal
import time


SODDIR="/home/cgray/silicon_on_demand"
JOBDIR="%s/jobs" % SODDIR

USE_TFTP = True

boards = ["sb-01", "sb-02"]

def sighup_handler(signal, frame):
    # this method defines the handler i.e. what to do
    # when you receive a SIGHUP
    print("%s:SIGHUP received" % sys.argv[0])


def fix_args(args):
    if isinstance(args, list):
        return str(" ".join(args))
    else:
        return args

def get_runfile(opts, board = None):
    if (opts.board is not None):
        board = opts.board

    if (board is None):
        return None

    return "%s/run.%s" % (SODDIR, board)
        
def reasonfile(board):

    return "%s/%s.offline" % (SODDIR, board)
    
# filename routines
def fdone(job):
    if (isinstance(job, dict)):
        return "%s/job.done" % job['path']
    else:
        return "%s/job.done" % job
    
def frestart(job):
    return "%s/restart.fail" % job['path']

def fcooked(job):
    return "%s/minicom-log.txt" % job['path']

def fpost(job):
    return "%s/postscript-log.txt" % job['path']

def fraw(job):
    return "%s/minicom-log" % job['path']

# claim file specifies that one of the servers is running
# this job so other servers shoudl not pick it up
def fclaim(job):
    return "%s/job.claimed" % job['path']

def time_key(job):
    return job['submit_time']

def load_job(opts, name, want_done):
    path = "%s/%s/job.js" % (JOBDIR, name)
    done = "%s/%s/job.done" % (JOBDIR, name)

    # if we want done jobs, make sure we filter
    is_done = os.path.exists(done)
    want_waiting = (not want_done)
    waiting = (not is_done)

    if (want_done and waiting):
        return None

    # if we do want done jobs, make sure it's done
    if (is_done and want_waiting):
        return None

    if (opts.verbose):
        print("job %s" % name)
        print("path %s" % path)
        print("done %s" % done)
        print("is_done: %s" % is_done)
        print("want_waiting: %s" % want_waiting)
        print("want_done: %s" % want_done)
        print("waiting: %s" % waiting)
    
    try:
        fl = open(path)
        job = json.load(fl)
    except:
        return None

    job['log_type'] = "no log"
    job['log'] = "no log found"
    job['reason'] = "???"
    job['raw_log'] = None
    job['cooked_log'] = None
    
    if (os.path.exists(fraw(job))):
        job['raw_log'] = fraw(job)
        job['log'] = job['raw_log']
        job['log_type'] = 'raw log'

    if (os.path.exists(fcooked(job))):
        job['cooked_log'] = fcooked(job)
        job['log'] = job['cooked_log']
        job['log_type'] = 'log'
            
    if (os.path.exists(fpost(job))):
        job['post_log'] = fpost(job)
    else:
        job['post_log'] = None
        
    try:
        if (os.path.exists(fdone(job))):
            job['reason'] = open(fdone(job)).readline().strip()
    except:
        return job

    return job

def job_matches_id(opts, job, jobid):

    if ("jobid" in job):
        # match the whole job id
        if (job['jobid'] == jobid):
            return True

        # match the unique string
        if (job['jobid'][-6:] == jobid):
            return True
        
    # match the whole path
    if (job['path'] == jobid):
        return True

    return False

def job_is_claimed(job):

    fname = fclaim(job)
    if (os.path.exists(fname)):
        return True
    return False
    
def is_owner(opts, job, all=None):
    if (opts.all or all):
        return True
    if (opts.uname == job["user"]):
        return True

    return False

def job_list(opts, done=False, all=None):
    names = os.listdir(JOBDIR)
    l = []

    for n in names:
        job = load_job(opts, n, done)
        if (job is None):
            continue

        if (not is_owner(opts, job, all)):
            continue
        l.append(job)

    return l

def print_status(opts, job):

    funos = job.get('funos')
    args = job.get('args')
    board = job.get('board')
    if (board is None):
        board = ""
    else:
        board = "<%s> " % board
    print("%s %s- %s -- %s" % (job['path'], board, funos, args))
    if (job['raw_log'] is not None):
        if (os.path.exists(fclaim(job))):
            claim = open(fclaim(job)).read()
        else:
            claim = "<unknown>"
        print("   -->  %s logging to %s" % (claim, job['raw_log']))
    if (opts.verbose):
        is_done = os.path.exists(fdone(job))
        print("   --> job is %s" % "DONE!" if is_done else "not done")
        

def print_results(job):

    if ("jobid" in job):
        print("jobid: %s" % job['jobid'])
    else:
        print("jobid: %s" % job['path'])
    print("funos: %s -- %s" % (job.get('funos'), job.get('args')))
    print("reason: %s" % job['reason'])
    print("%s: %s" % (job['log_type'], job['log']))
    if (job['post_log'] is not None):
        print("postscript log: %s" % job['post_log'])

    print()
    
def done_jobs_by_date(opts, all=None):
    # get it
    l = job_list(opts, done=True, all=all)

    # sort it
    l.sort(key=time_key)

    return l[-opts.num_done:]

def job_list_by_date(opts, all=None):

    # get it
    l = job_list(opts, done=False, all=all)

    # sort it
    l.sort(key=time_key)

    return l

def unclaimed_job_list_by_date(opts, all=None):
    ls = job_list_by_date(opts, all)
    rls = []

    for l in ls:
        if job_is_claimed(l):
            continue
        if (l.get("board", opts.board) != opts.board):
            continue
        rls.append(l)

    return rls
    
def maybe_install_funos(opts, funos, suffix):

    # do whatever
    if (not USE_TFTP):
        return funos

    os.system("mkdir -p /home/mboksanyi/tftpboot/%s" % opts.uname)

    binname = os.path.split(funos)[-1]
    ofunos = funos
    funos = "%s/%s-%s" % (opts.uname, suffix, binname)

    cmd = "cp %s /home/mboksanyi/tftpboot/%s" % (ofunos, funos)
    # print cmd
    os.system(cmd)
    
    return funos

def mkjob(opts, email, funos,  args):
    # make a pathname    
    uname = opts.uname
    now = datetime.datetime.now()
    now = now.replace(microsecond=0)
    dstr = now.isoformat('.')
    dstr = dstr.replace(":", ".")
    prefix = "%s-%s-" % (dstr, uname)
    if (opts.suffix is None):
        path = tempfile.mkdtemp(dir=JOBDIR, prefix=prefix)
        suffix = path.split("-")[-1]
    else:
        path = "%s/%s%s" % (JOBDIR, prefix, opts.suffix)
        suffix = opts.suffix
        os.mkdir(path)
        
    print("path is %s" % path)

    jobid = path.split("/")[-1]

    # make it world readable
    os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    # stuff a blank by default into run_job
    if (email is None):
        email = ""

    # create a json for it
    d = {}
    d['jobid'] = jobid
    d['user'] = uname
    if (funos is not None):
        funos = maybe_install_funos(opts, funos, suffix)
        d['funos'] = funos
        d['args'] = fix_args(args)
    d['emails'] = email
    d['path'] = path
    d['submit_time'] = dstr
    if (opts.xargs is not None):
        d['xargs'] = opts.xargs
    if (opts.timeout is not None):
        d['timeout'] = int(opts.timeout)
    if (opts.board is not  None):
        d['board'] = opts.board
    if (opts.delay is not None):
        d['delay'] = opts.delay

    print("job is %s/job.js" % path)
    fl = open("%s/job.js" % path, 'w')
    json.dump(d, fl, indent=4, sort_keys=True)
    fl.close()

    print("Submitted jobid %s" % jobid)

def rmjob(opts, jobid):
    l = job_list_by_date(opts, all=True)

    if (len(l) == 0):
        print("No jobs to kill")
        return

    if ((jobid == "next") and ("jobid" in l[0])):
        jobid = l[0]['jobid']

    for job in l:
        if (job_matches_id(opts, job, jobid)):
            os.system("echo killed > %s" % fdone(job['path']))
            print("killed %s" % job['path'])
            return

    print("job not found")

def restartjob(opts, jobid):
    print("scanning last %d jobs to restart..." % opts.num_done)
    l = done_jobs_by_date(opts)

    for job in l:
        if (job_matches_id(opts, job, jobid)):
            donefile = fdone(job)
            print("Removing done file %s" % donefile)
            os.system("rm %s" % donefile)
            if (os.path.exists(donefile)):
                print("ERROR: job file couldn't be removed")
            else:
                print("Job restarted")
            return

    print("No matching job found")
    
def lsjobs(opts):

    # check server status
    if (opts.board is None):
        servers = boards
    else:
        servers = [opts.board]
    for srv in servers:
        runfile = get_runfile(opts, srv)
        if (os.path.exists(runfile)):
            print("status %s: silicon on demand server should be online" % srv)
        else:
            reason = "<no reason given>"
            if (os.path.exists(reasonfile(srv))):
                reason = open(reasonfile(srv)).read()
            print("status %s: OFFLINE: %s" % (srv, reason))
        
    l = job_list_by_date(opts, all=True)

    print("== %d waiting jobs (next first) ==" % len(l))
    for job in l:
        print_status(opts, job)

    if (opts.num_done > 0):
        l = done_jobs_by_date(opts)
        print()
        print("== Last %d completed jobs (most recent last) ==" % len(l))
        for job in l:
            print_results(job)

def tailjob(opts):
    l = job_list_by_date(opts, all=True)
    if (len(l) == 0):
        print("no jobs")

    job = l[0]
    
    if (os.path.exists(job['log'])):
        os.system("tail -f %s" % job['log'])
    else:
        print("job log file '%s' does not exist" % job['log'])
        
def lessjob(opts, args):

    l = done_jobs_by_date(opts)

    job = None
    if (len(args) == 0):
        job = l[-1]
    else:
        for j in l:
            if (job_matches_id(opts, j, args[0])):
                job = j
                break
                
    if (job is None):
        print("job not found. Increase n?")
        return
    
    os.system("less %s" % job['log'])

def _getlogin():

    login = os.environ.get("USER")
    if (login is None):
        login = os.environ.get("LOGNAME")
    if (login is None):
        login = os.getlogin() # may be wrong?!
    
    return login
    
def online_server(opts):

    if (opts.board is None):
        print("must specify a board to online")
        return

    fname = get_runfile(opts)
    open(fname, 'w').write("online")
    if (os.path.exists(reasonfile(opts.board))):
        os.remove(reasonfile(opts.board))
    

def offline_server(opts, reason):
    if (opts.board is None):
        print("must specify a board to offline")
        return

    fname = get_runfile(opts)
    if (not os.path.exists(fname)):
        print("server %s already offline? trying anyway" % opts.board)
    else:
        os.remove(fname)
    if (os.path.exists(reasonfile(opts.board))):
        os.remove(reasonfile(opts.board))
    open(reasonfile(opts.board), 'w').write("%s: %s" % (opts.uname, reason))
    
def sod_client():
    parser = optparse.OptionParser(usage="usage: %prog [options] action [arguments]")
    parser.add_option("-u", "--uname", action="store", default=None)
    parser.add_option("-a", "--all", action="store_true", default=False)
    parser.add_option("-n", "--num-done", action="store", type="int", default=5)
    parser.add_option("-t", "--timeout", action="store", default="5")
    parser.add_option("-x", "--xargs", action="store", default=None)
    parser.add_option("-v", "--verbose", action="store_true", default=False)
    parser.add_option("-s", "--suffix", action="store", default=None)
    parser.add_option("-e", "--email", action="append", default=[])
    parser.add_option("-b", "--board", action="store", default=None)
    parser.add_option("-D", "--delay", action="store", type="int", default=None)

    (opts, args) = parser.parse_args()

    if (opts.uname is None):
        try:
            opts.uname = _getlogin()
            print("Running as user %s" % opts.uname)
        except:
            opts.uname = "secret_squirrel"

    if (opts.board is not None):
        if (opts.board not in boards):
            print("unknown board %s" % opts.board)
            sys.exit(1)
            
    if len(args) < 1:
        parser.error("missing action, one of: submit, list, kill, restart, tail, less")
        sys.exit(1)

    action = args[0]
    args = args[1:]

    # make email addresses a string
    if (len(opts.email) == 0):
        email = None
        epath = "/home/%s/.forward" % opts.uname
        if (not os.path.exists(epath)):
            epath = "/home/%s/.silicon_email" % opts.uname
        if (os.path.exists(epath)):
            lines = file(epath).readlines()
            lines = list(map(str.strip, lines))
            email = " ".join(lines)
    else:
        email = " ".join(opts.email)
            
    if (action == "submit"):
        if (len(args) < 1):
            parser.error("submit expects a funos  gzip file")

        funos = args[0]
        args = args[1:]

        mkjob(opts, email, funos, args)
    elif (action == "submit_noboot"):
        if (len(args) > 0):
            parser.error("submit_noboot expects no args")

        mkjob(opts, email, None, None)
    elif (action == "list"):
        lsjobs(opts)
    elif (action == "tail"):
        tailjob(opts)
    elif (action == "less"):
        if (len(args) > 1):
            parser.error("less expects zero or one id")
        lessjob(opts, args)
    elif (action == "restart"):
        if (len(args) != 1):
            parser.error("kill expects an id")

        restartjob(opts, args[0])
    elif (action == "kill"):
        if (len(args) != 1):
            parser.error("kill expects an id")

        rmjob(opts, args[0])
    elif (action == "online"):
        online_server(opts)
    elif (action == "offline"):
        if (len(args) == 0):
            parser.error("please specify a reason")
        offline_server(opts, " ".join(args))
    else:
        parser.error("unknown action %s" % action)


def claim_job(job, board):
    fname = fclaim(job)
    try:
        print("open %s" % fname)
        f = os.open(fname, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        print("write %s" % board)
        os.write(f, "%s" % board)
        print("done")
        return job
    except:
        print("except fail")
        return None
    
        
def main(opts, joblist):

    if (len(joblist) == 0):
        print("No job to run")
        return

    print("%s claiming job %s" % (opts.board, joblist[0]['path']))
    job = claim_job(joblist[0], opts.board)
    if (job is None):
        print("Failed to claim job, trying again...")
        return
    
    print("Running the following job...")
    print_status(opts, job)

    delay = job.get("delay", 0)
    if (delay > 0):
        print("%s: Delaying for %d seconds...\n" % (datetime.datetime.now().replace(microsecond=0).isoformat(), delay))
        open(fraw(job), 'w').write("delaying for %s seconds\n" % delay)
        time.sleep(delay)
        print("%s: Continuing job\n" % datetime.datetime.now().replace(microsecond=0).isoformat())

    
    # default 5 minute timeout
    timeout = job.get("timeout", "")
    if (timeout != ""):
        timeout = "-t %s" % timeout
    
    if ("funos" in job):
        funos = job["funos"]
        args = fix_args(job['args'])
    else:
        funos = ""
        args = ""

    xargs = ""
    if ("xargs" in job):
        xargs = job["xargs"]

    tftp = ""
    if (USE_TFTP):
        tftp = "-F"
        
    os.system("(cd %s && %s/run_job.py -r --board=%s %s %s %s %s -- %s)" % (job['path'], SODDIR, opts.board, tftp, timeout, xargs, funos, args))

    if (not os.path.exists(frestart(job))):
        os.system("(echo -n 'Finished at ' && date) > %s" % fdone(job['path']))
        print("job done in %s" % job['path'])
        os.system("rm -f %s" % fclaim(job))
    else:
        print("job in %s requires restart" % job['path'])
        os.system("rm %s" % frestart(job))
        os.system("rm -f %s" % fclaim(job))
        return
    
    email = job.get("emails", "")
    if (isinstance(email, list)):
        email = str(" ".join(email))
    if (email != ""):
        # reload the job now to get the logs
        job = load_job(opts, job['jobid'], True)
        
        subject = "[silicon on demand] job %s complete" % job['jobid']

        body = "log path<br />%s/minicom-log<br />" % job["path"]
        
        if (os.path.exists(job['log'])):
            out = subprocess.Popen(['%s/uart2html.py' % SODDIR, job['log']], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.STDOUT)
            stdout,stderr = out.communicate()
            body += stdout
        else:
            body += "\ncouldn't dump logfile"

        fl = open("%s/email-body.txt" % job["path"], "w")
        fl.write(body)
        fl.close()

        cmd = "cat %s/email-body.txt | mail -r charles.gray+silicon@fungible.com -s '%s' -a 'Content-Type: text/html; charset=UTF-8' %s" % (job['path'], subject, email)
        print("Here goes nothing...")
        os.system(cmd)
        print("Sent?")
        
        

    

if (__name__ == "__main__"):

    # ignore hangups from child job management
    signal.signal(signal.SIGHUP, sighup_handler)

    parser = optparse.OptionParser(usage="usage: %prog [options] action [arguments]")
    parser.add_option("-u", "--uname", action="store", default=None)
    parser.add_option("-a", "--all", action="store", default=True)
    parser.add_option("-v", "--verbose", action="store", default=False)
    parser.add_option("-b", "--board", action="store", default=None)

    (opts, args) = parser.parse_args()

    if (opts.uname is None):
        try:
            opts.uname = _getlogin()
            print("Running as user %s" % opts.uname)
        except:
            opts.uname = "secret_squirrel"

    if (opts.board not in boards):
        print("invalid board specified: %s. Pick one of: %s" % (opts.board, boards))
        sys.exit(1)

    run_next = False
    if ((len(args) > 0) and (args[0] == "run_next")):
        run_next = True
    
    joblist = unclaimed_job_list_by_date(opts)

    # see if we're a single instance
    if (run_next):
        print("silicon on demand running next job")
        main(opts, joblist)
        print("returning")
        sys.exit(0)

    # main server loop
    runfile = get_runfile(opts)
    print("Starting silicon on demand server...")
    while (True):
        # see if we should terminate
        if (not os.path.exists(runfile)):
            print("%s: no run file at %s, waiting" %  (time.strftime('%Y-%m-%d %H:%M:%S'), runfile))
            time.sleep(20)
            continue

        # get the latest job list
        joblist = unclaimed_job_list_by_date(opts)
        
        # see if there's even a job to run
        if (len(joblist) == 0):
            time.sleep(2)
            continue

        # call out to run the next job
        os.system("%s --board=%s run_next" % (sys.argv[0], opts.board))
        print("Silicon on demand server pausing for next job...")
        time.sleep(5)

