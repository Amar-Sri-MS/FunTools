#!/usr/bin/env python3
#
# Copyright (c) Fungible Inc, 2019
#
import argparse
import errno
import json
import os
import platform
import shutil
import socket
import sys
import subprocess
from io import StringIO
import tempfile

from contextlib import closing

BASE_URL = 'http://dochub.fungible.local/doc/jenkins'

# release image json contains a few fourcc code for images
# that we don't want to be used for upgrade, eg. fun1, boot
# or images that should not be automatically upgraded, such
# as eepr
KNOWN_IMAGES = {'husd', 'husm', 'husc', 'hbsb',
                'sbpf', 'kbag', 'host', 'emmc',
                'mmc1', 'nvdm', 'scap', 'pufr',
                'frmw'}
# these images require async upgrade
ASYNC_ONLY_IMAGES = {'nvdm', 'scap'}
# these images do not report sdk version correctly, so ignore
# the reported version
IGNORE_VERSION_IMAGES = {'nvdm', 'scap'}
# only update the following images if they are reported
# as existant, if not reported then they are not supported
# properly in FunOS
UPGRADE_IF_PRESENT_IMAGES = {'nvdm', 'scap'}
# these upgrades sometimes randomly fail, their upgrade
# success is not critical, so only log the error but do not
# report the whole upgrade as failing. A failure can be later
# noticed during upgrade success verification
IGNORE_ERRORS_IMAGES = {'nvdm', 'scap'}

EXIT_CODE_OK = 0
EXIT_CODE_ERROR = 1
EXIT_CODE_DOWNGRADE_ATTEMPT = 2

class UpgradeException(Exception):
    # base class for all custom exceptions
    pass

class DowngradeAttemptException(UpgradeException):
    pass

def run(cmdlist, stdout=None):
    print("EXEC: {}".format(" ".join(cmdlist)))
    return subprocess.call(cmdlist,stdout=stdout)

def run_check(cmdlist, stdout=None, stderr=None):
    print("EXEC: {}".format(" ".join(cmdlist)))
    return subprocess.call(cmdlist,stdout=stdout,stderr=stderr)

def wget(url, outfile=None):
    if outfile:
        run(['wget', '-O', outfile, '-q', url])
    else:
        run(['wget', '-q', url])


def prepare_offline(args, path='', select=None):
    rel = lambda f: os.path.join(path, f)

    if args and args.upgrade_file:
        f = args.upgrade_file.split('=', 1)
        return {f[0]: rel(f[1])}

    images = {}
    with open(rel('image.json'), 'r') as f:
        release = json.load(f,encoding='ascii')

        if not select:
            if args.image_type:
                select=lambda k,v: rel(k) if v.get('image_type') == args.image_type else None
            else:
                select=lambda k,v: rel(k)

        for outfile, v in release['signed_images'].items():
            value = select(outfile, v)
            if not images.get(v['fourcc']) and value:
                images[v['fourcc']] = value

        for outfile, v in release.get('signed_meta_images',{}).items():
            value = select(outfile, v)
            if not images.get(v['fourcc']) and value:
                images[v['fourcc']] = value

        images['emmc'] = select('emmc_image.bin', release['signed_images']['boot.img.signed'])
        images['mmc0'] = select('mmc0_image.bin', release['signed_images']['boot.img.signed'])
        images['mmc1'] = select('mmc1_image.bin', release['signed_images']['boot.img.signed'])

    return images

def using_custom_funcp(args):
    return args.image_url == BASE_URL and args.arch == 'posix'


def prepare(args):
    """
        Prepare workspace
         - download latest FunCP release from dochub
         - download latest flash images from dochub
    """

    if args.offline:
        return prepare_offline(args)

    funcp_file = 'funcp.{}.tgz'.format(args.arch)
    libfunq_file = 'libfunq.{}{}.tgz'.format(args.arch, '_palladium' if args.arch == 'posix' else '')

    SDK_FLASH_PATH = '/{}/funsdk/{}/Linux'.format(args.sdk_devline, args.version)
    release_file = '{}_dev_signed.tgz'.format(args.chip)

    if args.image_url == BASE_URL:
        url = args.image_url + SDK_FLASH_PATH
    else:
        url = args.image_url

    files = {
        release_file : url,
    }

    if using_custom_funcp(args):
        files[funcp_file] = url
        files[libfunq_file] = url

    for f, url in files.items():
        wget(url + '/' + f)
        run(['tar', '-xf', f])

    release_dir = '{}_dev_signed'.format(args.chip)

    if os.path.isdir(release_dir):
        return prepare_offline(args, release_dir)
    else:
        return prepare_offline(args)


def run_upgrade(args, release_images):
    """
        Perform firmware upgrade
    """
    if isinstance(args.pci_devid, list):
        for pci_devid in args.pci_devid:
            pcidevs_string = subprocess.check_output(['lspci', '-d', pci_devid, '-mmn'])
            if pcidevs_string:
                break
    else:
        pcidevs_string = subprocess.check_output(['lspci', '-d', args.pci_devid, '-mmn'])

    sudo = [] if platform.machine() == 'mips64' else ['sudo']
    if args.offline or not using_custom_funcp(args):
        if platform.machine() == 'mips64':
            # defaults for CCLinux
            binpath = '/usr/bin'
            ldpath = []
            funqpath = '/usr/bin'
        else:
            # defaults for COMe
            binpath = os.path.join(args.offline_root, 'FunControlPlane', 'bin')
            ldpath = ['LD_LIBRARY_PATH=${{LD_LIBRARY_PATH}}:{}'.format(
                    os.path.join(args.offline_root, 'FunControlPlane', 'lib'))]
            funqpath = binpath
    else:
        newroot = os.path.join(args.ws, 'FunSDK/host-drivers/x86_64/user/{}_palladium'.format(args.arch))
        binpath = os.path.join(args.ws, 'FunCP', 'build', args.arch, 'bin')
        ldpath = ['LD_LIBRARY_PATH=${{LD_LIBRARY_PATH}}:{}:{}'.format(
                    os.path.join(args.ws, 'build', args.arch, 'lib'),
                    os.path.join(newroot, 'lib'))]
        for p in (binpath,
                  os.path.join(newroot, 'bin')):
            if os.path.isfile(os.path.join(p, 'funq-setup')):
                funqpath = p
                break
        else: # this is for ... else statement
            raise(Exception("funq-setup not found!"))
    res = 0

    if args.upgrade_file:
        args.upgrade = release_images.keys()

    for arg in args.upgrade:
        if not os.path.isfile(release_images[arg]):
            raise(Exception("Upgrade image for '{}' not found in upgrade bundle".format(arg)))

    if not pcidevs_string:
        raise(Exception("No Fungible devices detected on PCI"))

    pcidevs = [dev.split()[0].decode('ascii') for dev in pcidevs_string.splitlines()]

    def pcidev_unbind(dev):
        if args.bind:
            run(sudo + ldpath + \
                [os.path.join(funqpath, 'funq-setup'),
                'unbind', '"vfio"', dev])

    def fourcc_eq(dpu_fourcc, host_fourcc):
        return (dpu_fourcc == host_fourcc) or \
                ((host_fourcc == 'sbpf') and \
                 (dpu_fourcc == 'pufr' or dpu_fourcc == 'frmw')
                )

    for dev in pcidevs:
        # BIND
        # bind the vfio ff00 function of the F1's PCI driver, which corresponds
        # to the HCI interface that the upgrade code uses. Loop over all of interfaces
        # found, as when executed on FS1600's COMe, there are 2 F1s connected.
        # When run on CCLinux, there should be only one interface found.
        if args.bind:
            cmd = sudo + ldpath + \
                [os.path.join(funqpath, 'funq-setup'),
                'bind', 'vfio', dev]
            try:
                run_check(cmd, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                print(e.output.decode())
                res |= e.returncode
                continue

    if res:
        for dev in pcidevs:
            pcidev_unbind(dev)
        raise(Exception("Failed to bind PCI VFIO"))

    upgrade_fourccs = {}
    downgrade_fourccs = {}

    v = args.version
    if v == 'latest':
        v = 2**32 # force upgrade to whatever latest happens to be
                    # version is 32-bits, so 2**32 will indicate that
                    # an upgrade is always required
    else:
        v = int(v)

    # exit code 64 indicates unrecognized arg
    with open(os.devnull, 'w') as devnull:
        have_async_fwupgrade = subprocess.call(sudo + ldpath + \
                [os.path.join(binpath, 'fwupgrade'), '--async'],
                stdout=devnull, stderr=devnull) != 64

    for dev in pcidevs:
        fwinfo = json.loads(subprocess.check_output(sudo + ldpath + \
                [os.path.join(binpath, 'fwupgrade'),
                '-a', '-d', dev]))
        dev_downgrade_fourccs = set()
        dev_upgrade_fourccs = list()

        if args.upgrade_auto:
            release_images_fourccs = set(release_images.keys()) & KNOWN_IMAGES

            if not have_async_fwupgrade:
                release_images_fourccs = release_images_fourccs - ASYNC_ONLY_IMAGES

            if len(fwinfo) == 0:
                dev_upgrade_fourccs = list(release_images_fourccs)
            else:
                for fw in fwinfo['firmwares']:
                    # 'status' is not reported before build 8654, so do not assume
                    # it's always there. If frmw version is < 8654 but FunOS is newer,
                    # then 'status' field exists and is set to 'unknown'

                    # async upgrade (even if supported by fwupgrade app) may not work
                    # correctly on builds around 11500, all branches have the necessary
                    # fixes in after 11500, so only attempt to upgrade async images for
                    # those systems
                    if fw['fourcc'] == 'mmc1' and fw['version'] < 11500 and \
                        fw.get('status','active') in ['active', 'unknown']:
                        release_images_fourccs = release_images_fourccs - ASYNC_ONLY_IMAGES

                    # firmwares older than 9531 do not recognize kbag or husc as
                    # valid identifiers, so do not attempt to program these images, as this
                    # will result in an error.
                    if fw['fourcc'] == 'frmw' and fw['version'] < 9531 and \
                       fw.get('status','active') in ['active', 'unknown']:
                        release_images_fourccs = release_images_fourccs - { 'kbag', 'husc' }

                    # FunOS doesn't recognise incompatible devices and currently the
                    # only way we find out that it's a different device type is when
                    # the upgrade fails. The only externally visible method to determine
                    # incompatibility is by checking existing fw version - if it is 24.6C
                    # (9324) then this means it is an incompatible device and we should not
                    # attempt upgrading it
                    if fw['fourcc'] == 'nvdm' and fw['version'] == 9324:
                        release_images_fourccs = release_images_fourccs - {'nvdm'}

                    if fw['fourcc'] in release_images_fourccs:
                        if fw['version'] < v or fw['fourcc'] in IGNORE_VERSION_IMAGES:
                            # current version is lower than one found, so add
                            dev_upgrade_fourccs.append(fw['fourcc'])
                        elif fw['version'] > v and \
                             fw.get('status','active') in ['active', 'unknown']:
                            # current active version is higher, so potential downgrade
                            dev_downgrade_fourccs.add(fw['fourcc'])
                        else:
                            # Versions are equal or inactive image, ignore
                            pass

                for fw in fwinfo['firmwares']:
                    release_images_fourccs.discard(fw['fourcc'])

                if not 'pufr' in dev_upgrade_fourccs and \
                   not 'frmw' in dev_upgrade_fourccs:
                       release_images_fourccs.discard('sbpf')

                # emmc and mmc1 images are 'special', ie. they should always exist in flash and
                # should only be updated if they exist so the rule below for adding any new and
                # yet unprogrammed image types should not apply. Hence always remove them from
                # the new set to prevent attempted upgrades.
                release_images_fourccs.discard('mmc1')
                release_images_fourccs.discard('emmc')

                for fw in release_images_fourccs:
                    if fw not in dev_upgrade_fourccs:
                        if fw not in UPGRADE_IF_PRESENT_IMAGES:
                            dev_upgrade_fourccs.append(fw)

                dev_upgrade_fourccs = list(set(dev_upgrade_fourccs))
                try:
                    # to work around a bug in sbp upgrade ensure that
                    # kbag is the last in list (fixed in 9589)
                    dev_upgrade_fourccs.remove('kbag')
                    dev_upgrade_fourccs.append('kbag')
                except ValueError:
                    pass

                # Remove frmw and pufr individual upgrades - there should be no
                # units with firmware that still accept it. They may have been added
                # to the list as these fourccs are reported by the DPU, but
                # they are upgraded via 'sbpf' fourcc
                try:
                    dev_upgrade_fourccs.remove('frmw')
                    dev_upgrade_fourccs.remove('pufr')
                    dev_downgrade_fourccs.remove('frmw')
                    dev_downgrade_fourccs.remove('pufr')
                except:
                    pass

        else:
            for fourcc in set(args.upgrade):
                for fw in fwinfo['firmwares']:
                    if fourcc_eq(fw['fourcc'], fourcc):
                        if fw['version'] < v or fw['fourcc'] in IGNORE_VERSION_IMAGES:
                            dev_upgrade_fourccs.append(fourcc)
                        elif fw['version'] > v and \
                             fw.get('status','active') in ['active', 'unknown']:
                            # current active version is higher, so potential downgrade
                            dev_downgrade_fourccs.add(fourcc)
                        else:
                            # Versions are equal or inactive image, ignore
                            pass
                        break
                else:
                    # also update if fourcc doesn't exist yet
                    dev_upgrade_fourccs.append(fourcc)

        upgrade_fourccs[dev] = dev_upgrade_fourccs
        downgrade_fourccs[dev] = dev_downgrade_fourccs

        print("Final list of images to upgrade for {}: {}".format(dev, upgrade_fourccs[dev]))
        print("List of images to maybe downgrade for {}: {}".format(dev, downgrade_fourccs[dev]))

    if any(downgrade_fourccs.values()) and not args.downgrade and not args.dry_run:
        for dev in pcidevs:
            pcidev_unbind(dev)
        raise DowngradeAttemptException()

    for dev in pcidevs:
        for fourcc in upgrade_fourccs[dev]:
          cmd = sudo + ldpath + \
                  [os.path.join(binpath, 'fwupgrade'),
                  '--image', release_images[fourcc], '-f', fourcc, '-d', dev]
          if args.active:
              cmd.append('--active')
          if args.downgrade:
              cmd.append('--downgrade')
          if fourcc in ASYNC_ONLY_IMAGES:
              cmd.append('--async')

          if not args.dry_run:
            # CHECK CURRENT VERSION AND UPGRADE
            print('Upgrading {} with {}'.format(fourcc, release_images[fourcc]))
            try:
                subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                # depending on the fw version, pufr/frmw/sbpf upgrades may fail
                # need to parse error log - if error reported by sbp is '2', then
                # this is the expected error and no need to panic
                print(e.output.decode())
                if e.returncode == errno.EIO and \
                   fourcc in ('pufr', 'frmw', 'sbpf') and \
                   (('Error in upgrade handling: 2' in e.output.decode()) or \
                        ('Error in upgrade handling: 33554432' in e.output.decode())):
                    print('If you see this error message, do not report it, it is expected')
                elif fourcc in IGNORE_ERRORS_IMAGES:
                    print('Upgrade of {} failed, ignoring this error'.format(fourcc))
                else:
                    res |= e.returncode
          else:
            print("Would execute {}".format(cmd))


        # GET ALL FIRMWARE VERSIONS
        if args.version_check:
            cmd = sudo + ldpath + \
                [os.path.join(binpath, 'fwupgrade'),
                '-a', '-d', dev]
            try:
                run_check(cmd, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                print(e.output.decode())
                res |= e.returncode
                pass

        # GET ALL FIRMWARE VERSIONS - STORE TO FILE AND UPDATE FW DB
        if not args.no_server_update:
          with tempfile.NamedTemporaryFile() as f:
            run(sudo + ldpath + \
                    [os.path.join(binpath, 'fwupgrade'),
                    '-a', '-d', dev], stdout=f)
            os.fsync(f)
            # strip garbage from output file ... workaround until FunCP is rebuilt
            # and we get a fixed
            run(['sed', '-i', '/^devname/d', f.name])

            try:
                # somewhat hacky way to get our machine name,
                # but hostname is not reliable as multiple
                # COMes have the same ...
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                try:
                    s.connect(('fun-on-demand-01',9501))
                    machine = socket.gethostbyaddr((s.getsockname()[0]))[0]
                    s.close()
                    machine = machine.replace('.fungible.local','')
                except:
                    pass

                # if there was no name found or the name doesn't contain any numbers
                # it's most likely a generic name like Fun or FunServer, so ignore it
                if not filter(str.isdigit, machine):
                    machine=''

                if not machine:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    try:
                        s.connect(('fun-on-demand-01',9501))
                        ip = s.getsockname()[0]
                        iface = ''
                        # get the device MAC address ... check for the interface
                        # we used for connecting to the server and then get its mac
                        with closing(StringIO(subprocess.check_output(
                                    ['ip', '-f', 'inet', '-o', 'addr']).decode())) as ifaces:
                            for i in ifaces:
                                if ip+'/' in i:
                                    iface = i.split()[1]
                                    break

                        if iface:
                            with open('/sys/class/net/{}/address'.format(iface),'r') as f_mac:
                                machine = f_mac.read().strip()

                        s.close()
                    except Exception as e:
                        print(e)

                print("using {} as machine id".format(machine))
                if machine:
                    run(['curl', '-X', 'POST', '--data', '@{}'.format(f.name),
                        'http://fun-on-demand-01:9501/store?machine={}:{}&key=firmware'.format(machine,dev)])
            except Exception as err:
                print(err)
                pass

    for dev in pcidevs:
        pcidev_unbind(dev)

    if res:
        raise(Exception("Errors occured during upgrade"))

# return all valid upgrade images available in 'path'
def get_current_upgrade_images(path, select):
    images = prepare_offline(None, path, select)
    return { key: images[key] for key in KNOWN_IMAGES if key in images }

def main():
    tmpws = None
    arg_parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    arg_parser.add_argument('--ws', action='store', metavar='path',
            help='workspace path, temp location will be used if not specified or'
                 '<offline-root>/funos if offline is set')
    arg_parser.add_argument('--arch', action='store', choices=['mips64', 'posix'],
            default='mips64' if platform.machine() == 'mips64' else 'posix',
            help='ControlPlane architecture')

    upgrade_group = arg_parser.add_mutually_exclusive_group()
    upgrade_group.add_argument('-u', '--upgrade', action='append', metavar='FOURCC',
            default=[], help='Specify fourcc of fw to upgrade')
    upgrade_group.add_argument('-U', '--upgrade-if-needed', action='store_true',
            dest='upgrade_auto',
            help='Upgrade fws that are older than new version')
    upgrade_group.add_argument('--upgrade-file', metavar='FOURCC=FILENAME',
            dest='upgrade_file',
            help='Specify fourcc=filename pair to upgrade from a specified file')

    arg_parser.add_argument('--image_url', default=BASE_URL,
                            help='Specify alternate URL for image location')
    arg_parser.add_argument('--sdk_devline', default='master',
                            help='Specify FunSDK development line to use')
    arg_parser.add_argument('-v', '--version',
            default='latest', help='Specify FunSDK version to use, number or \'latest\'.')

    arg_parser.add_argument('--downgrade', action='store_true',
            help='Attempt to perform a firmware downgrade')

    arg_parser.add_argument('--no-server-update',
            action='store_true', help='Do not send firmware information to db server')

    arg_parser.add_argument('--dry-run', action='store_true',
            help='Do all the checks, but do not perform upgrade. Implies --no-server-update')

    arg_parser.add_argument('--offline', action='store_true',
            help='Do not download any images, assume everything is available locally')

    arg_parser.add_argument('--offline-root', default="/opt/fungible",
            help='Location of the ControlPlane firmware')

    arg_parser.add_argument('--no-bind', dest='bind', action='store_false',
            help='Do not bind/unbind PCIe vfio interface')

    arg_parser.add_argument('--active', action='store_true',
            help='Attempt to upgrade active image')

    arg_parser.add_argument('--chip', choices=['f1', 's1'],
            default='f1', help='Target chip')

    arg_parser.add_argument('--pci-devid', default=['1dad:0105:', '1dad:0005:', '1dad::1000'],
            help='PCI device ID to use for upgrades')

    arg_parser.add_argument('--force', action='store_true',
            help='Force upgrade, do not ask any questions')

    arg_parser.add_argument('--select-by-image-type', dest='image_type',
            help='Select image by image_type')

    arg_parser.add_argument('--no-version-check', action='store_false',
            dest='version_check',
            help='Skip current version query')

    arg_parser.add_argument('--check-image-only', action='store_true',
            help='Do not perform upgrade, only check if a given image type is present in package')

    args, unknown = arg_parser.parse_known_args()

    if unknown:
        # for compatibility with various util scripts allow unknown arguments
        # to be passed, this is especially useful if new arguments are added
        # and generic scripts cannot use those args until support for them
        # is added
        print("WARNING: Unhandled arguments found: {}".format(unknown))

    if args.downgrade and not args.force:
        try:
            # always use python3 input
            # python3/input == python2/raw_input
            input = raw_input
        except NameError:
            pass

        sys.stdout.write("Attempting a downgrade of {active} image.\n"
                     "This is not guaranteed to work across all release versions.\n"
                     "Are you sure? [Yes/No] ".format(
                    active="active" if args.active else "inactive"))
        sys.stdout.flush()
        conf = input()
        if conf != 'Yes':
            print("Aborted by user")
            return

    if args.ws is None:
        if args.offline:
            args.ws = os.path.join(args.offline_root, 'funos')
        else:
            tmpws = tempfile.mkdtemp()
            args.ws = tmpws
    else:
        try:
            os.makedirs(args.ws)
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass

    if args.dry_run or args.offline:
        args.no_server_update = True

    os.chdir(args.ws)
    os.putenv('WORKSPACE', args.ws)

    print('Using {} as workspace'.format(args.ws))

    try:
        release_images = prepare(args)
        if args.check_image_only:
            i = { k:release_images.get(k) for k in args.upgrade if release_images.get(k) }
            sys.exit(EXIT_CODE_OK if len(i) == len(args.upgrade) else EXIT_CODE_ERROR)

        run_upgrade(args, release_images)
    except DowngradeAttemptException:
        sys.exit(EXIT_CODE_DOWNGRADE_ATTEMPT)
    except Exception as e:
        print(e)
        sys.exit(EXIT_CODE_ERROR)
    finally:
        if tmpws:
            print('Workspace cleanup, remove temp directory')
            shutil.rmtree(tmpws)


if __name__ == '__main__':
    main()
