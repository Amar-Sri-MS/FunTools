#!/usr/bin/env python3
#
# run_f1.py: Run binary on Fun-on-demand.  For now, only run F1 jobs.
#
# This is a reduced version of the run_emu.py script, intended for the single
# binary provided to Fun-on-demand.
#
# TODO(bowdidge): Support for Palladium.  Requires installing SBP files.
#
# For F1, provided binary must be funos-f1.stripped, built with
#     make MACHINE=f1 SIGN=1

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
try:
    import configparser  # python 3
except ImportError:
    import configparser as configparser # python 2.7

# Only use libraries from Python - don't import any of our own
# helpers, or non-default packages.  This code will need to run on
# other systems, and we should minimize additional requirements.

# True if job should not make permanent changes.
dryrun = False

# Set this flag if you are a robot that might be running when a human
# isn't present.  We might ask you to stop if you or another robot is
# misbehaving.
robot = False

# Default remote run-on-demand host.
DEFAULT_FUN_ON_DEMAND = 'fun-on-demand-01'

# Emulation_target values for real hardware.
HARDWARE_TARGETS = ['F1', 'S1']

# Hardware models URL.
HARDWARE_MODELS_URL = 'http://fun-on-demand-01:9004/hardware_models'
ROBOT_CONTROL_URL = 'http://fun-on-demand-01:9001/robotstate'

# Temporary key for timeout value.  We'll interpret it once we know
# where we're running.
TEMP_TIMEOUT_KEY = 'temp_timeout'

# Maximum length of bootargs that run_f1 will accept. The actual limit
# is u-boot's limit of 1024 characters in a command, but fun-on-demand
# tacks on a few hundred chars to the user bootargs for various reasons.
MAX_BOOTARG_LEN = 512

# Map from key used in scheduled execution params files to the keys
# used in Palladium-on-demand job files.
key_map = {'EXTRA_EMAIL': 'email',
           'HW_MODEL': 'hardware_model',
           'RUN_TARGET': 'emulation_target',
           'HW_VERSION': 'hardware_version',
           'PCI_MODE': 'pci_mode',
           'REMOTE_SCRIPT': 'remote_script',
           'NETWORK_MODE': 'network_mode',
           'NETWORK_SCRIPT': 'network_script',
           'CENTRAL_SCRIPT': 'central_script',
           'TAGS': 'tags',
           'PRIORITY': 'priority',
           'BOOTARGS': 's/w arg',
           'NOTE': 's/w note',
           'HBM_DUMP': 'hbm_dump',
           'ROOTFS_IMAGE_DIR': 'rootfs_image_dir',

           # These arguments require some extra processing after.
           # Must be post-processed to timeout_msecs or timeout_mins.
           'MAX_DURATION': TEMP_TIMEOUT_KEY,

           # These arguments are not used in run_f1 and are omitted.
           'DISABLE_ASSERTIONS': None,
           'AT': None,
           'FAST_EXIT': None,
           'NAME': None,
}

# Fields we likely don't have, but which should at least have an empty
# value.
REQUIRED_FIELDS = ['hardware_version', 'jenkins_url', 'jenkins_job',
                   'jenkins_job_url', 'jenkins_build_number', 'pci_mode',
                   'network_mode', 'uart_mode', 'uart_script', 'hbm_dump',
                   'wu_trace']

priority_map = {'low_priority': 0, 'normal_priority': 1,
                'high_priority': 2}

QUEUE_MANAGER_DEFAULT = 'http://fun-on-demand-01.fungible.local:9001'

class QueueManagerInterface(object):
    """Hide queries to queue manager.

    This makes it easier to mock.
    """
    def __init__(self, url=QUEUE_MANAGER_DEFAULT):

        self.url = url

    def enqueue_job(self, dest_root):
        """Asks QueueManager to enqueue the job provided in dest_root.

        Returns {'job_id': job_id, 'job_dir': '/path-to-fun-on-demand-dir'}
        or None if enqueue failed.
        """

        # Fun-on-demand's queue manager will enqueue job, and will
        # move spec file to correct name.
        sys.stderr.write('Sending request to enqueue job.\n')
        posthash = {'dir': dest_root}
        # The 'dir' field is passed in the 'data' field as a hash.
        #   Curl_json() urlencodes the hash and appends it to the URL.
        #   Sending it this way tells curl_json it is a POST request.
        response = curl_json(self.url + '/enqueue', data=posthash)
        if not response or not 'job_id' in response:
            sys.stderr.write('Failed to enqueue job.\n')
            return None
        try:
            job_id = response['job_id']
            if job_id == -1:
                sys.stderr.write("Failed to enqueue job: %s\n" % response['msg'])
                return None
            final_dir = response['job_dir']
            sys.stderr.write('Enqueued as job %d in directory %s\n'
                             % (job_id, final_dir))
        except Exception as e:
            sys.stderr.write('Corrupt response for enqueue: %s\n' % e)
            sys.stderr.write(out + "\n")
            shutil.rmtree(dest_root)
            return None
        return job_id, final_dir

    def get_job_status(self, job_id):
        """Returns all details on specified job.

        Returns dictionary provided by Palladuum Jobs website.

        Returns {} if an error occurred.
        """
        response = curl_json('http://palladium-jobs.fungible.local:8080'
                             '/job/%d?format=json' % job_id, timeout='60')
        if not response:
            sys.stderr.write('problems getting job status\n')
        return response


# Stolen from status_server/pal_lib.py
def RunCommandOnServer(cmd_args, user, server, ssh_help=False, get_stderr=True):
    """Runs a single command on a server.
    Returns return code and output.
    Exits immediately if the server could not be reached.
    """
    global dryrun

    if dryrun:
        # TODO(bowdidge): Handle multiple commands.
        cmd_args = ['echo'] + cmd_args

    cmd = ['ssh', '-o', 'BatchMode=yes',
           '-o', 'StrictHostKeyChecking=no',
           '-l', user, server] + cmd_args
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT if get_stderr else None)
    except subprocess.CalledProcessError as e:
        if ssh_help:
            sys.stderr.write("Error: ssh to %s returned %d.\n"
                             "Please make sure that you can ssh without a password to host '%s' "
                             "as user '%s'.\n"
                             "The message was: %s\n" % (server, e.returncode, server, user, e.output))
        else:
            sys.stderr.write('Error: ssh to %s returned %d\n' %
                             (server, e.returncode))
            sys.stderr.write('Output: %s\n' % e.output)
        return (e.returncode, e.output)
    return (0, out)

def RunCommand(cmd_args, get_stderr=True):
    """Runs a single command on local machine.
    Returns return code and output.
    Exits immediately if the server could not be reached.
    """
    global dryrun

    if dryrun:
        # TODO(bowdidge): Handle multiple commands.
        cmd_args = ['echo'] + cmd_args

    try:
        out = subprocess.check_output(cmd_args, stderr=subprocess.STDOUT if get_stderr else None)
    except subprocess.CalledProcessError as e:
            sys.stderr.write('Error: command %s returned %d\n' %
                             (server, e.returncode))
            sys.stderr.write('Output: %s\n' % e.output)
            return (e.returncode, e.output)
    return (0, out)


class CopyExecutor(object):
    """Abstract away operations for putting together a job.

    run_f1.py enqueues jobs by building up a job directory in a temp
    directory on a lab machine, then asking for the job to be enqueued.
    Fun-on-demand then copies the directory into its own directories
    so that it owns all the files.

    This class hides details of creating the job directory and creating
    the files.  If run_f1.py is running on a lab machine, it creates the
    file locally; if not, it does remote operations to create the directory
    on a lab machine.
    """

    def __init__(self, dryrun=False,
                 fun_host=None, remoteuser=None):
        """Creates a CopyExecutor.

        If fun_host is not None, then assume run_f1.py is not on a
        system visible to Fun-on-demand, and that the temp directory needs
        to be on a lab server.

        dryrun: True if we should not do anything permanent.
        fun_host: name of remote host to copy files (if not local).
        remoteuser: login for remotehost (if not local).
        """
        self.dryrun = False
        self.is_remote = not os.path.exists('/home/robotpal')
        self.fun_host = fun_host
        self.remoteuser = remoteuser

        # Location of temp directory.
        self.dest_root = None

    def get_dest_root(self):
        """Returns name of temporary directory for assembling job.

        File will be on self.fun_host if doing a remote enqueue.
        """
        return self.dest_root

    def make_dir(self):
        """Creates a temporary directory to copy into.

        Returns True if directory was created.
        """
        if self.dryrun:
            sys.stderr.write('Would create temp dir in home dir.\n')
            self.dest_root = '/tmp/not_a_real_directory'
        elif self.is_remote:
            cmd = ['mktemp', '-p', '/tmp', '-d',
                   "tmp_run_f1-%s.XXXXXX" % self.remoteuser]
            (ret, dest_root) = RunCommandOnServer(cmd,
                                                  self.remoteuser,
                                                  self.fun_host,
                                                  ssh_help=True,
                                                  get_stderr=False)
            if ret:
                sys.stderr.write("remote mktemp command failed.\n")
                self.dest_root = None
                return None
            self.dest_root = dest_root.rstrip()
            if 'tmp_run_f1-' not in self.dest_root:
                # Protect against something stupid like dest_root = '/'
                sys.stderr.write('Unknown problems creating directory! %s\n')
                return False

            # Make sure directory and files will be readable by robotpal.
            cmd = ['chmod', 'a+rx', dest_root]
            (ret, out) = RunCommandOnServer(cmd,
                                            self.remoteuser,
                                            self.fun_host,
                                            ssh_help=True,
                                            get_stderr=False)
            if ret:
                sys.stderr.write('unable to make temp dir readable: %s' %
                                 out)
                return False

            # Make directory for binary blobs.
            cmd = ['mkdir', '-p', os.path.join(self.dest_root, 'blobs')]
            print(cmd)
            (ret, out) = RunCommandOnServer(cmd,
                                            self.remoteuser,
                                            self.fun_host,
                                            ssh_help=True,
                                            get_stderr=False)
            if ret:
                sys.stderr.write('unable to make dir for blobs: %s' %
                                 out)
                return False

            cmd = ['chmod', 'a+rx', dest_root]
            (ret, out) = RunCommandOnServer(cmd,
                                            self.remoteuser,
                                            self.fun_host,
                                            ssh_help=True,
                                            get_stderr=False)
            if ret:
                sys.stderr.write('unable to make blobs dir readable: %s' %
                                 out)
        else:
            self.dest_root = tempfile.mkdtemp(prefix='run_f1_',
                                        dir=os.getenv('HOME'))
            os.chmod(self.dest_root, 0o755)
            blobs_dir = os.path.join(self.dest_root, 'blobs')
            os.mkdir(blobs_dir)
            os.chmod(blobs_dir, 0o755)

        return True

    def copy_file(self, source_path, dest_file, scp_compress=False):
        """Copy the specified file to a specific path.

        source_path: relative path to file to copy.
        dest_file path to final location, relative to self.dest_root.
        scp_compress: True if files should be compressed when copied.

        Returns False if copy failed.
        """
        global dryrun

        dest_path = os.path.join(self.dest_root, dest_file)
        if dryrun:
            sys.stderr.write('Would copy %s to %s\n' % (source_path,
                                                        dest_path))
        elif self.is_remote:
            dest = '%s@%s:%s' % (self.remoteuser, self.fun_host, dest_path)
            cmd = ['scp', '-q', '-o', 'ForwardX11=no']
            if scp_compress is True:
                cmd.extend(['-C'])
            cmd.extend([source_path, dest])
            try:
                out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
                RunCommandOnServer(['chmod', 'g+r', dest_path],
                                   self.remoteuser, self.fun_host)
            except Exception as e:
                sys.stderr.write('scp command failed: %s' % e)
                return False
        else:
            try:
                shutil.copy(source_path, dest_path)
                # Make sure readable by others.
                mode = os.stat(dest_path).st_mode
                mode |= 0o444
                os.chmod(dest_path, mode)
            except Exception as e:
                sys.stderr.write('Errors copying file to job directory: %s\n'
                                 % e)
                return False

        return True


    def copy_dir(self, source_path, dest_dir, scp_compress = False):
        """Copy the specified file to a specific path.

        source_path: relative path to file to copy.
        dest_dir: name of directory to create in job directory, relative
        to self.dest_root.

        Returns False if copy failed.
        """
        global dryrun
        global scpcompress

        dest_path = os.path.join(self.dest_root, dest_dir)
        if dryrun:
            sys.stderr.write('Would copy %s to %s\n' % (source_path,
                                                        dest_path))
        elif self.is_remote:
            dest = '%s@%s:%s' % (self.remoteuser, self.fun_host, dest_path)
            cmd = ['scp', '-q', '-o', 'ForwardX11=no', '-r']
            if scp_compress:
                cmd.extend(['-C'])
            cmd.extend([source_path, dest])
            print(cmd)
            try:
                out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
                # Owner: read write, execute only on directories.
                # Group: read, execute only on directories.
                RunCommandOnServer(['chmod', '-R', 'u=rwX,g=rX,o=',
                                    dest_path],
                                   self.remoteuser, self.fun_host)
            except Exception as e:
                sys.stderr.write('scp command failed: %s' % e)
                return False
        else:
            try:
                shutil.copytree(source_path, dest_path)
                os.system('chmod -R u=rwX,g=rX,o= %s' % dest_path)
            except Exception as e:
                sys.stderr.write('Errors copying file to job directory: %s\n'
                                 % e)
                return False

        return True

    def cleanup(self):
        """Deletes the temporary directory created for the job."""
        if dryrun:
            sys.stderr.write('Would delete temp directory here.\n')
        elif self.is_remote:
            RunCommandOnServer(['rm', '-rf', self.dest_root],
                               self.remoteuser, self.fun_host)
            pass
        else:
            shutil.rmtree(self.dest_root)


class FunOnDemandJob(object):
    """
    Set up arguments for a Fun-on-demand job and starts it running.

    Fun-on-demand jobs can be defined in three different ways:
    * params file (same as Jenkins scheduled jobs)
    * jobspec file (from a past job)
    * dictionary of options from the command line.

    The caller should run one of the parse_* methods to get arguments
    defined, then call run() to start the job.

    FunOnDemandJob will know that it needs to copy the spec file and any
    scripts.  Caller is responsible for specifying the binary:
    job.add_file_to_copy('/path/to/binary', 'funos-f1.stripped')

    Fun-on-demand expects that the destination binary name be
    funos-f1.stripped.
    """
    def __init__(self, models_dict,
                 queue_manager_interface_class=QueueManagerInterface):

        # True if nothing permanent should be done.
        self.models_dict = models_dict

        # Dictionary of values for jobspec file.
        self.spec_dict = {}

        # Individual files to copy into job directory.
        # Array of (file, dest_name) pairs.
        self.files_to_copy = []

        # Directory trees to copy into job directory.
        # Array of (source directory, end directory) pairs.
        self.dirs_to_copy = []

        # Should we explicitly compress before copying?
        # Better for slow links, bad for fast.
        self.scp_compress = False

        # Job id of enqueued job, or None if not enqueued.
        self.lsf_job_id = None

        self.queue_manager_interface = queue_manager_interface_class()

        # Assume account on lab machine has same name.
        self.remoteuser = get_user_login()
        self.fun_host = DEFAULT_FUN_ON_DEMAND

        # List of names of binary chip architectures we've seen.
        # ['f1', 's1']
        self.binary_architectures_seen = []

    def add_binary(self, os_image):
        """Add the OS binary to the list of files to copy."""
        # TODO(bowdidge): pass the name of the binary as a new arg
        # so we don't need to care about the filename.
        model_name = self.spec_dict['hardware_model']
        model_dict =self.models_dict.get(model_name)
        if not model_dict:
            sys.stderr.write('Unknown hardware model %s', model_name)

        emulation_target = model_dict.get('emulation_target', 'F1')

        os_image_basename = os.path.basename(os_image)
        if os_image_basename.startswith('funos-f1'):
            architecture = 'f1'
            binary_target = 'F1'
        elif os_image_basename.startswith('funos-s1'):
            architecture = 's1'
            binary_target = 'S1'
        else:
            raise Exception('No idea how to handle binary %s' % os_image)

        if architecture in self.binary_architectures_seen:
            sys.stderr.write('Already seen binary for architecture %s' %
                             architecture)
            return False

        final_binary = 'funos-%s.stripped' % architecture
        self.add_file_to_copy(os_image, final_binary)
        if emulation_target == binary_target:
            # Binary for the primary architecture for the test.
            self.spec_dict['binary_name'] = final_binary
        self.binary_architectures_seen.append(architecture)

        return True


    def parse_jobspec_file(self, filename, cmd_opts):
        """Generates a dictionary of job keys based on a Fun-on-demand
        jobspec file.

        Keys in produced dictionary should be Fun-on-demand keys for
        job file.  As this method is likely to parse files already
        processed by the Fun-on-demand system, its main function is to
        remove any runtime-generated params that should not be specified
        for newly created jobs

        filename: path to jobspec file
        cmd_opts: CommandLineOptions from user as a dictionary.  This will
                  be the output of vars(ArgumentParser), so argument names will
                  have dashed changed to underbar, etc.

        Returns False if file could not be opened. Single malformed lines are
        ignored.
        """
        result = {}
        lnum = 0
        if not os.path.exists(filename):
            sys.stderr.write('Unknown jobspec file %s\n' % filename)
            return False

        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                lnum += 1
                if not line or line.startswith('#'):
                    continue

                terms = line.split(':', 1)
                if len(terms) != 2:
                    sys.stderr.write('Invalid line %d.  '
                                     'Expect KEY : VALUE\n' % lnum)
                    continue
                key = terms[0].strip()
                value = terms[1].strip()

                if (key in REQUIRED_FIELDS or
                    key in list(key_map.values()) or
                    key in ['timeout_mins', 'timeout_msecs', 'emulation_pipeline']):
                    result[key] = value

            self.spec_dict = result
        if not self._find_scripts(os.path.dirname(filename)):
            return False

        return self._parse_opts_finalize(cmd_opts)

    def parse_params_file(self, filename, cmd_opts):
        """Generates a dictionary of job keys based on scheduled job file.

        Keys in produced dictionary should be Fun-on-demand keys for job file.

        filename: path to params file
        cmd_opts: CommandLineOptions providing user arguments for this job

        Returns False if errors when handling arguments.
        """
        result = {}
        lnum = 0

        if not os.path.exists(filename):
            sys.stderr.write('Unknown jobspec file %s\n' % filename)
            return False

        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                lnum += 1
                if not line or line.startswith('#'):
                    continue

                terms = line.split(':', 1)
                if len(terms) != 2:
                    sys.stderr.write('Invalid line %d.  '
                                     'Expect KEY : VALUE\n' % lnum)
                    continue
                key = terms[0].strip()
                value = terms[1].strip()

                # If the key is 'PRIORITY' and the value is a string priority
                # map it to the numeric priority value.
                if key == 'PRIORITY' and value in priority_map:
                    value = priority_map[value]

                # Generate the result job_spec here.
                if key in key_map and key_map[key]:
                    result[key_map[key]] = value

        if 'ROOTFS_IMAGE_DIR' in result:
            if not os.path.isdir(result['ROOTFS_IMAGE_DIR']):
                sys.stderr.write('No such directory for rootfs_image_dir: %s' % result['ROOTFS_IMAGE_DIR'])
            else:
                self.add_dir_to_copy(result['ROOTFS_IMAGE_DIR'], 'rootfs_image')

        # Post-process options we can't handle otherwise.
        if TEMP_TIMEOUT_KEY in result:
            if result.get('emulation_target', 'palladium') in HARDWARE_TARGETS:
                result['timeout_mins'] = result[TEMP_TIMEOUT_KEY]
            else:
                result['timeout_msecs'] = result[TEMP_TIMEOUT_KEY]
            del result[TEMP_TIMEOUT_KEY]

        # Fill in fields expected by Fun-on-demand if not already provided.

        for field in REQUIRED_FIELDS:
            if field not in result:
                result[field] = ''

        self.spec_dict = result

        path = os.path.dirname(os.path.realpath(filename))
        if not self._find_scripts(path):
            return False

        return self._parse_opts_finalize(cmd_opts)

    def parse_options(self, cmd_opts, boot_args):
        """Initializes a job based on CommandLineOptions only.


        Returns False if job could not be initialized.
        """
        model_dict = self.models_dict.get(cmd_opts.hardware_model)
        if not model_dict:
            sys.stderr.write('Unknown hardware model %s\n' %
                             cmd_opts.hardware_model)
            return False

        emulation_target = model_dict['emulation_target']

        priority_number = priority_map.get(cmd_opts.priority, 0)

        self.spec_dict = {'branch_funos': cmd_opts.branch_funos,
                          'email': cmd_opts.email,
                          'emulation_target': emulation_target,
                          'hardware_model': cmd_opts.hardware_model,
                          'hardware_version': '',
                          'hbm_dump': '',
                          'jenkins_build_number': '',
                          'jenkins_job': '',
                          'jenkins_job_url': '',
                          'jenkins_url': '',
                          'network_mode': '',
                          'pci_mode': '',
                          'priority': priority_number,
                          's/w arg': ' '.join(boot_args),
                          's/w note': cmd_opts.note,
                          's/w version': cmd_opts.hash_funos,
                          'tags': cmd_opts.tags,
                          'timeout_mins': cmd_opts.timeout_mins,
                          'uart_mode': '',
                          'uart_script': '',
                          'wu_trace': 0,
                          'stats': cmd_opts.stats
                          }
        # Look only in current directory for the script.
        self._find_scripts(None)

        return self._parse_opts_finalize(cmd_opts)

    def _override_options(self, cmd_opts):
        """Borrow options from command line that should supercede spec.

        This allows a user to specify new tags, alternate pipeline scripts,
        or different e-mail from a previously run job or params file.

        Only options that are normally None can be interpreted in this way.
        Options with defaults (such as priority) can't hint whether the
        user requested a different value.

        Also override some options which specify the environment.
        """
        if cmd_opts.tags:
            self.spec_dict['tags'] = cmd_opts.tags
        if cmd_opts.email:
            self.spec_dict['email'] = cmd_opts.email
        if cmd_opts.run_pipeline:
            self.spec_dict['emulation_pipeline'] = cmd_opts.run_pipeline
        if cmd_opts.note:
            self.spec_dict['s/w note'] = cmd_opts.note

        if cmd_opts.fun_host:
            self.fun_host = cmd_opts.fun_host
        if cmd_opts.remoteuser:
            self.remoteuser = cmd_opts.remoteuser

        # scp always based on command line / config file.
        self.scp_compress = cmd_opts.scp_compress

        # other_image gets copied over with name only.
        for other_image in cmd_opts.other_images:
            self.add_file_to_copy(other_image, os.path.basename(other_image))

        for blob in cmd_opts.blobs:
            self.add_file_to_copy(blob, os.path.join('blobs',
                                                     os.path.basename(blob)))

        if cmd_opts.rootfs_image_dir:
            self.add_dir_to_copy(cmd_opts.rootfs_image_dir,
                                 'rootfs_image')

    def _parse_opts_finalize(self, cmd_opts):
        """Perform any final work that is common to all arg input methods."""

        self._override_options(cmd_opts)
        self.add_enqueue_time()

        return self._check_arguments()

    def _check_arguments(self):
        """Adjust arguments and check for inappropriate values.

        Checks arguments that may be provided from the job spec file or
        params files.  Values coming only from the command line should
        be tested in CommandLineOptions.validate().
        """

        email = self.spec_dict.get('email')
        if email:
            mail_addresses = email.split(',')
            for mail_address in mail_addresses:
                if (not mail_address.endswith('fungible.com') and
                    not mail_address.endswith('fungible.local')):
                    sys.stderr.write('Bad e-mail: %s\n' % mail_address)
                    sys.stderr.write('fungible.com addresses only, please!\n')
                    return False

        boot_args = self.spec_dict.get('s/w arg')
        if boot_args and '--wulog' in boot_args:
            self.spec_dict['wu_trace'] = 1

        if boot_args and len(boot_args) > MAX_BOOTARG_LEN:
            sys.stderr.write('Provided boot args with length {} exceeds '
                             'maximum length of {} '
                             'characters\n'.format(len(boot_args),
                                                   MAX_BOOTARG_LEN))
            return False

        if self.spec_dict.get('emulation_target') not in HARDWARE_TARGETS:
            sys.stderr.write('run_f1.py only works for jobs running on '
                             'real F1 (emulation_target=F1).  Got %s' %
                             self.spec_dict.get('emulation_target'))
            return False

        if not self._fix_unicode_in_spec():
            return False

        # Check if the hardware_model was specified and is a known model.
        model_name = self.spec_dict['hardware_model']
        if model_name not in self.models_dict:
            sys.stderr.write("Hardware model '%s' is unknown.\n" %
                             model_name)
            return False

        return True

    def _fix_unicode_in_spec(self):
        """Replace unicode characters in sensitive fields with ASCII.

        Return False if any unicode chars were unable to be converted.

        Modifies self.spec_dict in place.
        """
        # Any fields that might get unicode chars in them but have
        # obvious intent should be entered here.  Start with
        # 'software_arg' AKA 's/w arg' which is Boot Args and
        # frequently gets unicode chars in it.
        fields_to_transform = ['s/w arg', 'tags']

        # Fix any known unicode issues before passing along.
        for field in fields_to_transform:
            if field in self.spec_dict and self.spec_dict[field]:
                self.spec_dict[field] = uTransform(self.spec_dict[field])

        # Check for any remaining invalid chars in self.spec_dict.
        for field in list(self.spec_dict.keys()):
            # Fail if we find any non-ASCII characters (chars not
            # between space and tilde inclusive).
            if self.spec_dict[field] and re.search(r'[^ -~]',
                                                   str(self.spec_dict[field])):
                sys.stderr.write('Job spec dictionary contains '
                                 'invalid chars in field "%s"\n' % field)
                return False

        return True

    def add_file_to_copy(self, source_filepath, dest_name):
        """Remember a file to copy over to Fun-on-demand.

        source_filepath: full path to file to copy
        dest_name: name of file in job directory.
        """
        if not (source_filepath, dest_name) in self.files_to_copy:
            self.files_to_copy.append((source_filepath, dest_name))

    def add_dir_to_copy(self, source_dir_path, dest_dir_path):
        """Remember to copy a directory over to Fun-on-demand.

        source_dir_path: path to directory tree to include.
        dest_dir_path: path to root of copied directory.
        """
        self.dirs_to_copy.append((source_dir_path, dest_dir_path))

    def has_setting(self, key):
        """Returns True if job dictionary has key defined."""
        return key in self.spec_dict

    def add_setting(self, key, value):
        """Adds a new key to the spec file for the job."""
        self.spec_dict[key] = value

    def add_enqueue_time(self):
        """Mark the time the job was enqueued."""
        now = int(time.time())
        self.add_setting('build_start_secs', now)
        # TODO(bowdidge): Move to queue manager's enqueue process.
        self.add_setting('queue_start_secs', now)

    def _find_script(self, script_type, source_dir):
        """Find the named script, and remember it for copying.

        We look both in source_dir and current_dir.

        script_type: key in spec dictionary for script
        source_dir: directory where spec came from.

        script may be relative to source_dir or current directory.
        """
        containing_dir = os.path.dirname(os.path.realpath(__file__))

        script_cmd = self.spec_dict.get(script_type)
        script_path = script_cmd.split(' ')[0]
        script_name = os.path.basename(script_path)

        potential_paths = []
        source_dir = source_dir or os.getcwd()

        potential_paths = [os.path.join(source_dir, script_path),
                           os.path.join(source_dir, script_name)]
        potential_paths += [os.path.join(os.getcwd(), script_path),
                            os.path.join(os.getcwd(), script_name)]
        potential_paths += [os.path.join(containing_dir, script_path),
                            os.path.join(containing_dir, script_name)]

        for path in potential_paths:
            if os.path.exists(path):
                self.add_file_to_copy(path, script_name)
                return True
        sys.stderr.write("Failed to find script file %s.\n" % script_name)
        return False

    def _find_scripts(self, source_dir):
        """Find any script files from the job.

        Checks the dictionary for the known scripts, then searches
        directories to find the script to copy.

        Returns False if any scripts could not be found.

        May rewrite the *_script keys to point at the correct one.
        """
        for script_type in ('remote_script', 'network_script',
                            'uart_script', 'central_script'):
            if script_type in self.spec_dict and self.spec_dict[script_type]:
                # Get remote script from either the current directory,
                # or (if a params file was provided) from the directory
                # containing the params file.
                if not self._find_script(script_type, source_dir):
                    sys.stderr.write("Failed to find %s.\n" % script_type);
                    return False
        return True

    def start_job(self):
        """Runs a Fun-on-demand job with the given parameters and files.

        Returns True if job was enqueued.

        LSF job id in self.lsf_job_id.
        Destination directory in self.dest_root.
        """
        global dryrun
        f, spec_temp_name = tempfile.mkstemp()
        self.write_spec(f)

        executor = CopyExecutor(dryrun=dryrun,
                          fun_host=self.fun_host,
                          remoteuser=self.remoteuser)
        if not executor.make_dir():
            sys.stderr.write('Problems creating temp dir for job. Stopping')
            return False

        # TODO(bowdidge): Copy additional files (disassembly, generated files,
        # etc) but only if we're sure they're for this binary.

        # Copy files over.
        for source_path, dest_name in self.files_to_copy:
            if not executor.copy_file(source_path, dest_name,
                                      scp_compress=self.scp_compress):
                sys.stderr.write('Problems copying file %s, stopping.' %
                                 source_path)
                return False

        for source_root, dest_name in self.dirs_to_copy:
            if not executor.copy_dir(source_root, dest_name,
                                     scp_compress=self.scp_compress):
                sys.stderr.write('Problems copying dir %s, stopping.' %
                                 source_root)

        # Copy spec file into place.
        dest_spec_file ='job.spec'
        ret = executor.copy_file(spec_temp_name, dest_spec_file)
        os.unlink(spec_temp_name)
        if not ret:
            sys.stderr.write('Problems copying file %s, stopping.' %
                             spec_temp_name)
            return False

        if dryrun:
            print('would enqueue now')
        else:
            dest_root = executor.get_dest_root()
            ret = self.queue_manager_interface.enqueue_job(dest_root)
            if not ret:
                sys.stderr.write('failed to enqueue job: urlopen failed\n')
                executor.cleanup()
                return False

            (self.lsf_job_id, job_dir) = ret

        executor.cleanup()
        return True

    def write_spec(self, fh):
        """ Writes a job spec file """
        for key in self.spec_dict:
            os.write(fh, '%s: %s\n' % (key, self.spec_dict[key]))
        os.close(fh)

    def wait_until_complete(self):
        """Returns job return node, or None if something went wrong."""
        print('Waiting for job to complete.')
        while True:
            time.sleep(30)
            ret = self.queue_manager_interface.get_job_status(self.lsf_job_id)
            if not ret:
                # Error.  Guess we'll wait.
                continue
            if 'job_dict' not in ret:
                # error. we'll wait.
                continue
            job_state = ret['job_dict'].get('state')
            if job_state == 'completed':
                return ret['job_dict'].get('return_code', None)
            # TODO(bowdidge): Time out?
        return None

    def wait_until_accepted(self):
        print('Waiting for job to be accepted.')
        while True:
            time.sleep(2)
            ret = self.queue_manager_interface.get_job_status(self.lsf_job_id)
            if not ret:
                # Error.  Guess we'll wait.
                continue
            if 'job_dict' not in ret:
                # error. we'll wait.
                continue
            job_state = ret['job_dict'].get('state')
            if job_state == 'accepted' or job_state == 'running' or job_state =='completed':
                sys.stderr.write('Job started')
                return
            # TODO(bowdidge): Time out?

    def get_job_status(self):
        """Returns information about the running job.

        Specifically, this returns the JSON served by the
        palladium-jobs job server.  It includes whether the job's running,
        whether it's completed, and console logs.
        """
        return self.queue_manager_interface.get_job_status(self.lsf_job_id)


def get_user_login():
    """Returns username of user running the script."""
    try:
        return os.getlogin()
    except OSError:
        return os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))


def curl_json(url, data=None, timeout='10'):
    """Curl a URL and return the parsed json response.
    Timeout = optional timeout value as a string.
    data = POST data.  Set to data='' and append the urlencoded '?X=Y' on the end of the url.
    Return {} if an error occurred.
    """
    try:
        if data == None:
            # GET request.
            req = urllib.request.Request(url)
        else:
            # POST request.
            url += '?%s' % urllib.parse.urlencode(data)
            req = urllib.request.Request(url, data='')
        out = urllib.request.urlopen(req, timeout=float(timeout)).read()
    except urllib.error.HTTPError as e:
        sys.stderr.write('Fetching HTTP URL failed: %s: %s\n' % (e.code, e.reason))
        return {'error': e.reason}
    except urllib.error.URLError as e:
        sys.stderr.write('Fetching URL failed: %s\n' % (e.reason))
        return {'error': e.reason}
    except Exception as e:
        sys.stderr.write("Fetching URL failed badly: %s\n" % e)
        sys.exit(6)
    try:
        response = json.loads(out)
    except ValueError as e:
        sys.stderr.write('json.loads() failed: %s\n' % e)
        return {'error': str(e)}

    return response


def get_robot_control_state(state_url=ROBOT_CONTROL_URL):
    """Get the Fun On Demand queue state.
    Return a hash describing the current state.
    Return {} if an error occurred.

    Currently possible states:
      robot_stop    robot_state    robot    non-robot
        False         OK            run       run
        True          STOP          exit      exit
        True          THROTTLE      exit      run
    """
    response = curl_json(state_url)
    if not response or not 'robot_stop' in response:
        sys.stderr.write('problems getting the robot state\n')
        return {}

    return response


def can_submit(is_robot):
    """Returns False if job shouldn't run because of limitations."""

    qState = get_robot_control_state()
    if not qState or not 'robot_stop' in qState:
        # If you cannot determine robot state, exit.
        sys.stderr.write("Unable to determine Fun On Demand queue state.")
        return False

    if is_robot and qState['robot_state'] == 'THROTTLE':
        # If you are a robot AND the state is 'THROTTLE', exit.
        sys.stderr.write("Fun On Demand queue is currently throttled!\n")
        sys.stderr.write("No 'robot' requests allowed!\n")
        return False
    elif qState['robot_state'] == 'STOP':
        # Robot or not, if state is 'STOP', exit.
        sys.stderr.write("Fun On Demand queue is currently stopped!\n")
        return False
    return True


def get_hardware_models(models_url=HARDWARE_MODELS_URL):
    """Get the list of harware models from the known location.
    Return it as a list of dicts.
    """
    response = curl_json(models_url)
    if not response or not 'hardware_models' in response:
        sys.stderr.write('problems getting hardware models\n')
        return []

    return response['hardware_models']

# Taken from FunDevelopment/jenkins/utils.py
# Dict of 1:>1 char translations.
uTransformDict = {
    "\u2014": "--",   # Emdash
    "\u2122": "(TM)", # Trademark
    "\u00ae": "(R)",  # Registered Trademark
}
# Tuple of 1:1 char translations.
uTransformTuple = [("\u00a0", " "),  # No-Break Space
                   ("\u2002", " "),  # En Space
                   ("\u2003", " "),  # Em Space
                   ("\u2004", " "),  # Three-Per-Em Space
                   ("\u2005", " "),  # Four-Per-Em Space
                   ("\u2006", " "),  # Six-Per-Em Space
                   ("\u2007", " "),  # Figure Space
                   ("\u2008", " "),  # Punctuation Space
                   ("\u2009", " "),  # Thin Space
                   ("\u200a", " "),  # Hair Space
                   ("\u200b", " "),  # Zero Width Space
                   ("\u2010", "-"),  # Hyphen
                   ("\u2013", "-"),  # Endash
                   ("\u2018", "'"),  # Left single quote => single quote
                   ("\u2019", "'"),  # Right single quote => single quote
                   ("\u201a", "'"),  # Single Low-9 quote => single quote
                   ("\u201b", "'"),  # Single High-Reversed-9 quote => single quote
                   ("\u201c", '"'),  # Left double quote => double quote
                   ("\u201d", '"'),  # Right double quote => double quote
                   ("\u201e", '"'),  # Double Low-9 quote => double quote
                   ("\u201f", '"'),  # Double High-Reversed-9 quote => double quote
                   ("\u2022", "*"),  # Bullet
                   ("\u202f", " "),  # Narrow No-Break Space
                   ("\u2060", " "),  # Word Joiner
]
# Create the table for .translate().
uTransformTable = dict((ord(From), To) for From, To in uTransformTuple)

def uTransform(uToTransform):
    """Convert commonly broken chars to their expected value."""
    origstr = uToTransform
    for c in list(uTransformDict.keys()):
        uToTransform = uToTransform.decode("utf-8").replace(c, uTransformDict[c]).encode("utf-8")
    # TODO(tbush): Don't 'ignore' failed encoded chars but handle them appropriately.
    newstr = uToTransform.decode("utf-8").translate(uTransformTable).encode("ascii","ignore")
    return newstr


def configfile_get(configfile, section, key, default):
    """Retrieve key from named section of a users' configuration file.

    configfile: configfile contents object.
    section: string name of section for key.
    key: named configuration value to return.
    default: value to use if key is not present.
    """
    result = default
    try:
        result = configfile.get(section, key)
    except NoSectionError as NoOptionError:
        pass
    finally:
        return result

def configfile_getboolean(configfile, section, key, default):
    """Retrieve key from named section of a users' configuration file.

    configfile: configfile contents object.
    section: string name of section for key.
    key: named configuration value to return.
    default: value to use if key is not present.
    """
    result = default
    try:
        result = configfile.getboolean(section, key)
    except NoSectionError as NoOptionError:
        pass
    finally:
        return result

class CommandLineOptions(object):
    """Read arguments from the command line and do minimal sanity checks.

    Also looks at config file for user; config file settings will be used
    if user does not provide options on command line.
    """

    def __init__(self, option_dict, configfile):
        """Set up CommandLineOptions.

        option_dict: dictionary of set values.
        configfile: ConfigParser object giving user's default settings.
        """
        username = get_user_login()
        self.email = None
        self.remoteuser = username
        self.fun_host = None
        self.scp_compress = False

        # Current environment gives us first choices.
        # We use configfile default if available.
        if configfile:
            self.email = configfile_get(configfile, 'user', 'email',
                                        self.email)
            self.remoteuser = configfile_get(configfile, 'user', 'remoteuser',
                                            self.remoteuser)
            self.fun_host = configfile_get(configfile, 'user', 'fun-host',
                                           self.fun_host)
            self.scp_compress = configfile_getboolean(
                configfile, 'network', 'scp-compress', False)

        # Use command line option_dict next.
        if option_dict.get('email') is not None:
            self.email = option_dict.get('email')
        if option_dict.get('remoteuser') is not None:
            self.remoteuser = option_dict.get('remoteuser')
        if option_dict.get('fun_host') is not None:
            self.fun_host = option_dict.get('fun_host')
        if option_dict.get('scp_compress') is not None:
            self.scp_compress = option_dict.get('scp_compress')

        self.timeout_mins = option_dict.get('duration')
        self.tags = option_dict.get('tags')
        self.note = option_dict.get('note')
        self.priority = option_dict.get('priority')
        self.robot = option_dict.get('robot')
        self.hardware_model = option_dict.get('hardware_model')
        self.params_file = option_dict.get('params_file')
        self.jobspec_file = option_dict.get('jobspec_file')
        self.run_pipeline = option_dict.get('run_pipeline')
        self.stats = option_dict.get('stats')
        self.publish = option_dict.get('publish')

        self.other_images = []
        self.blobs = []

        other_images = option_dict.get('other_images')
        if other_images:
            self.other_images = other_images.split(',')

        blobs = option_dict.get('blobs')
        if blobs:
            self.blobs = blobs.split(',')

        self.rootfs_image_dir = option_dict.get('rootfs_image_dir', None)

        # TODO(bowdidge): Snoop at git info to get version info for FunOS.
        self.branch_funos = '?'
        self.hash_funos = '?'

    def validate(self):
        """Checks whether command line arguments are sane.

        Checks that might need to be done on spec files should be done
        in FunOnDemandJob._check_validate()

        Returns False if execution shouldn't continue.
        """
        # Check command line options are valid.
        if self.timeout_mins < 1 or self.timeout_mins > 120:
            sys.stderr.write('--duration must be between 1 and 120 minutes.\n')
            return False

        # Check the priority string and map it to a priority number.
        if self.priority is not None and self.priority not in priority_map:
            sys.stderr.write('--priority must be high_priority, '
                             'normal_priority, or low_priority.\n')
            return False

        # Validate the parameters we were given.  Either from the
        # command line or the job_spec file or params file.
        if self.priority is not None:
            if priority_map.get(self.priority) == None:
                print('Unknown priority level %s' % self.priority)
                return False

        # Check if the params_file exists if it was specified.
        if self.params_file and not os.path.exists(self.params_file):
            sys.stderr.write("Missing params file '%s' specified.\n" %
                             self.params_file)
            return False

        # Check if the jobspec_file exists if it was specified.
        if self.jobspec_file and not os.path.exists(self.jobspec_file):
            sys.stderr.write("Missing jobspec file '%s' specified.\n" %
                             self.jobspec_file)
            return False

        # Check if the other images exist.
        for other_image in self.other_images:
            if not os.path.exists(other_image):
                sys.stderr.write("Missing other_image file '%s' specified.\n" %
                                 other_image)
                return False

        for blob in self.blobs:
            if not os.path.exists(blob):
                sys.stderr.write("Missing blob file '%s' specified.\n" %
                                 blob)
                return False

        if self.rootfs_image_dir and not os.path.isdir(self.rootfs_image_dir):
            sys.stderr.write("No directory for rootfs '%s' found.\n" %
                             self.rootfs_image_dir)
            return False

        if self.publish and not publish_checks():
            return False

        return True

def split_runf1_and_funos_args(my_argv):
    """Returns a tuple of (run_f1_args, funos_args)

    FunOS args are separated from run_f1 args by a -- separator.
    """
    if '--' not in my_argv:
        return my_argv, []

    index = my_argv.index('--')
    boot_args = my_argv[index+1:]
    my_argv = my_argv[:index]

    my_bootargs = []
    # Check for non-ascii in bootargs.
    for arg in boot_args:
        if not re.search(r'^[ -~]*$', arg):
            # See if we can fix it!
            arg = uTransform(arg)
            if not re.search(r'^[ -~]*$', arg):
                # Didn't get fixed.  Give up.
                sys.stderr.write('error: bootargs string "%s" '
                                 'has non-ascii characters.\n', arg)
                return False
        my_bootargs.append(arg)
    return my_argv, my_bootargs


def check_binary(binary_path):
    """Returns true if binary appears to be valid signed FunOS image.

    Check for all the common mistakes.
    """
    # Use file utility to guess at file contents.
    # Signed binaries show up as data, so we'll try to spot the alternatives.
    # TODO(bowdidge): Find more precise way to identify that a file is
    # a signed Elf MIPS binary.

    # Check if the os_image file exists.
    if not os.path.exists(binary_path):
        sys.stderr.write("Missing os_image file '%s'.\n" % binary_path)
        return False

    ret, out = RunCommand(['file', binary_path])
    if ret != 0:
        return False

    if 'ELF' in out:
        sys.stderr.write('File %s appears to be unsigned executable.\n'
                         'Please provide a signed binary.\n' % binary_path)
        return False

    if 'gzip compressed data' in out:
        sys.stderr.write('File %s appears to be a gzipped file.\n'
                         'Please provide an uncompressed signed binary.\n' %
                         binary_path)
        return False

    return True


def funos_image(image):
    supported = set([
        'funos-f1.signed',
        'funos-f1.stripped',
        'funos-f1-release.signed',
        'funos-s1.signed',
        'funos-s1.stripped',
        'funos-s1-release.signed'
    ])

    if os.path.basename(image) not in supported:
        msg = 'FunOS images must be one of: {}.\n'.format(",".join(supported))
        sys.stderr.write(msg)

        # Normally would raise argparse ArgumentError, but then it exits with 2
        # instead of 1, so to conform to specified return values for this
        # script, exit directly with 1.
        sys.exit(1)

    return image


def funos_image_unsigned(image):
    """
    Argparse type specification helper to verify that the argument provided for
    the --publish option is a valid unsigned image.
    """

    if not os.path.exists(image):
        msg = 'Unsigned image at {} not found.\n'.format(image)
        sys.stderr.write(msg)

        sys.exit(1)

    ret, out = RunCommand(['file', image])
    if ret != 0:
        msg = 'Failed to run file on image at {}.\n'.format(image)
        sys.stderr.write(msg)

        sys.exit(1)

    if 'ELF' not in out:
        msg = 'Image {} does not appear to be an unsigned executable.\n'
        sys.stderr.write(msg.format(image))

        sys.exit(1)

    return image


def get_silicon_models_dict():
    """ Get the silicon hardware models, keyed by the model name """
    model_list = get_hardware_models()
    models_dict = {}
    for model in model_list:
        if model['emulation_target'] in HARDWARE_TARGETS:
            models_dict[model['hardware_model']] = model
    return models_dict


def publish_checks():
    """
    Verify that WORKSPACE is set, and print the value.
    """

    workspace = os.environ.get("WORKSPACE")
    if not workspace:
        sys.stderr.write("Workspace isn't set, but --publish was provided.\n")
        return False

    sys.stderr.write("Using WORKSPACE={} for publishing.\n".format(workspace))

    return True


def publish_image(image):
    """
    Helper function to publish a binary using excat. The image is assumed to be
    at the provided path, and to be a valid unsigned image. If this fails, an
    error message is printed, but this does not affect the overall returncode
    of the script.

    This requires that the FunSDK in the workspace, that the WORKSPACE var be
    set, and that excat be in the given FunSDK.
    """

    path = os.path.expandvars('$WORKSPACE/FunSDK/bin/scripts/excat.py')
    executable = os.path.isfile(path) and os.access(path, os.X_OK)
    if not executable:
        sys.stderr.write("Can't find executable excat at {}\n".format(path))
        return

    cmd = [path, 'publish', image]

    if dryrun:
        sys.stderr.write('Would publish {} using excat.\n'.format(image))
    else:
        sys.stderr.write('Publishing {} using excat.\n'.format(image))

    RunCommand(cmd)


def main(args=sys.argv):
    # Validate arguments.
    global dryrun
    global tmp_scp_dir

    configfile = configparser.SafeConfigParser();
    configfile.read(os.path.expanduser("~/.runf1rc"))

    run_argv = list(map(uTransform, list(sys.argv)))
    run_argv, funos_boot_args = split_runf1_and_funos_args(run_argv)

    # Get the known hardware models and pick the ones we want.
    models_dict = get_silicon_models_dict()

    bootargs_help = """
Arguments after '--' are treated as boot arguments for FunOS.  Example:
  run_f1.py funos-f1.stripped -- test=unittest_test_empty --wulog

If you provide either --params-file or --jobspec-file, settings from those
files are used.  --tags, --note, --email, and --emulation_pipeline will
override settings in the files.

Return codes:
  0 = OK
  1 = Bad args
  2 = Remote setup failed
  3 = Arg checking failed
  4 = Fun On Demand queue stopped
  5 = Queueing of the job failed
  6 = Failed to get REST data

Some user default settings can be specified using an ini-like user
configuration file (~/.runf1rc). The following options are currently supported:
# ----------
[user]
remoteuser = remote user name
email = user@fungible.com
fun-host = servername
# ----------
Values specified in the config file are used as default if not specified
on cmdline. Values specified as cmdline args override the config file defaults.
"""
    parser = argparse.ArgumentParser(epilog=bootargs_help,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--dryrun', action='store_true',
                        help='do not enqueue jobs')
    parser.add_argument('--scp-compress', action='store_true', default=None,
                        help='compress scp xfers for very slow networks')
    parser.add_argument('--robot', action='store_true', default=False,
                        help='hint that job is scripted and may be run by badly-behaved robot.')
    parser.add_argument('--duration', action='store', default=5, type=int,
                        help='maximum duration in minutes for job: {1 - 120}')
    parser.add_argument('--priority', action='store', default='normal_priority',
                        help='job priority: {low,normal,high}_priority')
    parser.add_argument('--tags', action='store', default='',
                        help='mark job with given tags')
    parser.add_argument('--note', action='store', default='',
                        help='add a reminder note to help find the job')
    parser.add_argument('--email', action='store', default=None,
                        help='e-mail address to notify of job completion')
    parser.add_argument('--hardware-model', action='store',
                        default='F1',
                        help='hardware model / configuration for job. ')
    parser.add_argument('--run-pipeline', action='store',
                        default=None,
                        help='alternate version of Fun-on-demand scripts')
    parser.add_argument('--stats', action='store',
                        default='',
                        help='comma-separated list of additional statistics '
                        'to gather in telemetry.')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--params-file', action='store',
                        default=None,
                        help=('run from Jenkins scheduled job form.'
                              'params file takes precedence over any other '
                              'command-line flags.'))
    group.add_argument('--jobspec-file', action='store',
                        default=None,
                        help=('run from an existing Palladium-on-demand jobspec. '
                              'Jobspec file takes precedence over any other '
                              'command-line flags.'))

    parser.add_argument('os_image', nargs='+', type=funos_image,
                        help='FunOS stripped binaries to run')
    parser.add_argument('--publish', type=funos_image_unsigned,
                        help=('Publish an unsigned FunOS image using excat. '
                              'This requires FunSDK in $WORKSPACE.'))

    # Paths that add extra files to the job.
    parser.add_argument('--other-images', action='store',
                        help=('Comma-separated list of files to include in '
                              'the job directory.'))

    parser.add_argument('--blobs', action='store',
                        help=('Comma-separated list of files to be loaded as '
                              'blobs into FunOS.'))

    parser.add_argument('--rootfs-image-dir', action='store',
                        help=('path to directory containing tar files to '
                              'construct root filesystem for CC-Linux'))

    # Arguments affecting how we enqueue jobs / where we place files.
    parser.add_argument('--remoteuser', action='store', default=None,
                        help='User id to use for ssh to the remote system if not the current user.')
    parser.add_argument('--fun-host', action='store', default=None,
                        help='Fungible server to use for ssh to execute commands from')

    parser.add_argument('--wait-until-complete', action='store_true',
                        help='wait until job completes.')

    parser.add_argument('--wait-until-accepted', action='store_true',
                        help='wait until job is accepted.')

    # Parse all but binary name.
    options = parser.parse_args(run_argv[1:])

    if not dryrun:
        dryrun = options.dryrun

    command_line_options = CommandLineOptions(vars(options), configfile)
    if not command_line_options.validate():
        sys.exit(3)

    if not can_submit(command_line_options.robot):
        sys.exit(4)

    job = FunOnDemandJob(models_dict=models_dict)

    # TODO(bowdidge) Should error on boot args for params or jobspec files.
    if command_line_options.params_file:
        parse_ret = job.parse_params_file(command_line_options.params_file,
                                          command_line_options)
    elif command_line_options.jobspec_file:
        parse_ret = job.parse_jobspec_file(command_line_options.jobspec_file,
                                           command_line_options)
    else:
        parse_ret = job.parse_options(command_line_options, funos_boot_args)

    for image in options.os_image:
        if not check_binary(image):
            sys.stderr.write('Problems with binary, exiting.\n')
            sys.exit(1)

        if not job.add_binary(image):
            sys.stderr.write('Problems preparing binary %s' % image)
            sys.exit(1)

    if not parse_ret:
        sys.stderr.write('Problems parsing arguments, exiting.\n')
        sys.exit(1)

    ret = job.start_job()

    if not ret:
        sys.stderr.write('Fun-On-Demand job submit failed!\n')
        sys.exit(1)

    if options.publish:
        publish_image(options.publish)

    if options.wait_until_accepted:
        job.wait_until_accepted()

    if not options.wait_until_complete:
        # We've done enough.
        sys.exit(0)


    job.wait_until_complete()
    job_json = job.get_job_status()

    if 'job_dict' not in job_json:
        print('Malformed job status retrieved.')
        sys.exit(1)

    job_output = job_json.get('output_text')
    job_return_code = job_json.get('job_dict').get('return_code')
    job_return_msg = job_json.get('job_dict').get('return_code_msg')

    print(job_output)
    print('Job result: %d (%s)' % (job_return_code, job_return_msg))

    sys.exit(job_return_code)


if __name__ == '__main__':
    main()
