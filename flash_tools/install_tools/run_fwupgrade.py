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
import traceback
from contextlib import closing

try:
    # This is all under a try clause, as depending on FunOS version,
    # any or all of these modules could be missing ...
    sys.path.append('/usr/bin')
    import dpc_client
    import dpc_binary

    dpc = dpc_client.DpcClient(legacy_ok=False,
            unix_sock=True,
            encoder=dpc_binary.BinaryJSONEncoder())

    # Try to execute fw_upgrade version query. If it's implemented
    # and reports upgrade interface version 1 or higher, then the
    # upgrade can be performed using DPC. Otherwise the fwupgrade
    # script needs to use HCI-based fallback.
    res = dpc.execute('fw_upgrade', ['version'])

    if not res >= 1:
        raise RuntimeError("DPC upgrade not supported")
except:
    dpc = None
    pass

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
# these images should use async upgrade if supported
ASYNC_PREF_IMAGES = {'mmc1'}
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
# images to split into smaller chunks during upgrade
# (supported only in DPC mode)
SPLITTABLE_IMAGES = {'mmc1'}
SPLIT_SIZE = 2*1024*1024


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

def prepare(args):
    """
        Prepare workspace
         - download latest FunCP release from dochub
         - download latest flash images from dochub
    """

    if args.offline:
        return prepare_offline(args)

    SDK_FLASH_PATH = '/{}/funsdk/{}/Linux'.format(args.sdk_devline, args.version)
    release_file = '{}_dev_signed.tgz'.format(args.chip)

    if args.image_url == BASE_URL:
        url = args.image_url + SDK_FLASH_PATH
    else:
        url = args.image_url

    files = {
        release_file : url,
    }

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

    res = 0

    if args.upgrade_file:
        args.upgrade = release_images.keys()

    for arg in args.upgrade:
        if not os.path.isfile(release_images[arg]):
            raise Exception(f"Upgrade image for '{arg}' not found in upgrade bundle")

    if dpc:
        pcidevs = ['dpc']
    elif not pcidevs_string:
        raise Exception("No Fungible devices detected on PCI")
    else:
        pcidevs = [dev.split()[0].decode('ascii') for dev in pcidevs_string.splitlines()]
        binpath = '/usr/bin'
        funqpath = '/usr/bin'

    def pcidev_unbind(dev):
        if args.bind:
            run([os.path.join(funqpath, 'funq-setup'),
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
            cmd = [os.path.join(funqpath, 'funq-setup'),
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
        raise Exception("Failed to bind PCI VFIO")

    upgrade_fourccs = {}
    downgrade_fourccs = {}

    v = args.version
    if v == 'latest':
        v = 2**32 # force upgrade to whatever latest happens to be
                    # version is 32-bits, so 2**32 will indicate that
                    # an upgrade is always required
    else:
        v = int(v)

    if not dpc:
        # exit code 64 indicates unrecognized arg
        with open(os.devnull, 'w') as devnull:
            have_async_fwupgrade = subprocess.call(
                [os.path.join(binpath, 'fwupgrade'), '--async'],
                stdout=devnull, stderr=devnull) != 64

    for dev in pcidevs:
        if dpc:
            fwinfo = dpc.execute("fw_upgrade", ['get_versions'])
        else:
            fwinfo = json.loads(subprocess.check_output(
                [os.path.join(binpath, 'fwupgrade'),
                '-a', '-d', dev]))
        dev_downgrade_fourccs = set()
        dev_upgrade_fourccs = list()

        if args.upgrade_auto:
            release_images_fourccs = set(release_images.keys()) & KNOWN_IMAGES

            if not dpc and not have_async_fwupgrade:
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

        print(f"Final list of images to upgrade for {dev}: {upgrade_fourccs[dev]}")
        print(f"List of images to maybe downgrade for {dev}: {downgrade_fourccs[dev]}")

    if any(downgrade_fourccs.values()) and not args.downgrade and not args.dry_run:
        for dev in pcidevs:
            pcidev_unbind(dev)
        raise DowngradeAttemptException()

    for dev in pcidevs:
        for fourcc in upgrade_fourccs[dev]:
            if dpc:
                error = 0
                try:
                    file_size = os.path.getsize(release_images[fourcc])
                    split_size = SPLIT_SIZE if fourcc in SPLITTABLE_IMAGES else file_size
                    offset = 0

                    while offset < file_size:
                        dpc_params = {
                            'active' : bool(args.active),
                            'downgrade' : bool(args.downgrade),
                            'fourcc' : fourcc,
                            'offset' : offset
                        }

                        if not args.dry_run:
                            with open(release_images[fourcc], 'rb') as f:
                                f.seek(offset, os.SEEK_SET)
                                blob = dpc.dpc_blob_from_string(f.read(split_size))
                        else:
                            blob = f"blob for {release_images[fourcc]} offset {offset} size {split_size}"

                        command = [ 'upgrade', dpc_params, blob ]

                        if not args.dry_run:
                            resp = dpc.execute('fw_upgrade', command)
                            if resp['result'] != 0:
                                print(f"Upgrade of {fourcc}@{offset} failed: {resp['description']}")
                                raise RuntimeError(f"{fourcc}@{offset} failed: {resp['description']}")
                        else:
                            print(f"Would execute {command}")

                        offset += split_size

                except:
                    error = 1
                    if fourcc in IGNORE_ERRORS_IMAGES:
                        print(f"Upgrade of {fourcc} failed, ignoring this error")
                        error = 0
                    pass

                res |= error

            else: # !dpc
                cmd = [os.path.join(binpath, 'fwupgrade'),
                        '--image', release_images[fourcc], '-f', fourcc, '-d', dev]
                if args.active:
                    cmd.append('--active')
                if args.downgrade:
                    cmd.append('--downgrade')
                if fourcc in ASYNC_PREF_IMAGES and have_async_fwupgrade:
                    cmd.append('--async')
                elif fourcc in ASYNC_ONLY_IMAGES:
                    cmd.append('--async')

                if not args.dry_run:
                    # CHECK CURRENT VERSION AND UPGRADE
                    print(f"Upgrading {fourcc} with {release_images[fourcc]}")
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
                    print(f"Would execute {cmd}")


        # GET ALL FIRMWARE VERSIONS
        if args.version_check:
            if dpc:
                print(dpc.execute("fw_upgrade", ['get_versions']))
            else:
                cmd = [os.path.join(binpath, 'fwupgrade'),
                    '-a', '-d', dev]
                try:
                    run_check(cmd, stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as e:
                    print(e.output.decode())
                    res |= e.returncode
                    pass

    for dev in pcidevs:
        pcidev_unbind(dev)

    if res:
        raise Exception("Errors occured during upgrade")

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

    # no-server-update option doesn't do anything, currently kept for compatibility
    # with other scripts. to be removed.
    arg_parser.add_argument('--no-server-update',
            action='store_true', help='[ignored]')

    arg_parser.add_argument('--dry-run', action='store_true',
            help='Do all the checks, but do not perform upgrade.')

    arg_parser.add_argument('--offline', action='store_true',
            help='Do not download any images, assume everything is available locally')

    arg_parser.add_argument('--offline-root', default="/opt/fungible",
            help='Location of the ControlPlane firmware')

    arg_parser.add_argument('--no-bind', dest='bind', action='store_false',
            help='Do not bind/unbind PCIe vfio interface')

    arg_parser.add_argument('--active', action='store_true',
            help='Attempt to upgrade active image')

    arg_parser.add_argument('--chip', choices=['f1', 's1', 'f1d1'],
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
        print(f"WARNING: Unhandled arguments found: {unknown}")

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

    os.chdir(args.ws)
    os.putenv('WORKSPACE', args.ws)

    print(f"Using {args.ws} as workspace")
    print(f"Using {'DPC' if dpc else 'HCI'} interface")

    if dpc:
        args.bind = False
        args.pci_devid = []

    try:
        release_images = prepare(args)
        if args.check_image_only:
            i = { k:release_images.get(k) for k in args.upgrade if release_images.get(k) }
            sys.exit(EXIT_CODE_OK if len(i) == len(args.upgrade) else EXIT_CODE_ERROR)

        run_upgrade(args, release_images)
    except DowngradeAttemptException:
        sys.exit(EXIT_CODE_DOWNGRADE_ATTEMPT)
    except Exception as e:
        print(f"Upgrade error ... {e}")
        traceback.print_exc()
        sys.exit(EXIT_CODE_ERROR)
    finally:
        if tmpws:
            print("Workspace cleanup, remove temp directory")
            shutil.rmtree(tmpws)


if __name__ == '__main__':
    main()
