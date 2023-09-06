#!/usr/bin/env python3

""" Copyright (c) 2017-2020 Fungible, Inc. All Rights reserved """

import struct
import sys
import os
import configparser
import re
import json
import binascii
import argparse
import shutil
import firmware_signing_service as fsi
import key_replace as kr
import key_bag_create as kbc
import tempfile
import copy
import pprint

# image type is at 2 SIGNER_INFO size +  FW_SIZE + FW_VERSION
IMAGE_TYPE_OFFSET = 2048 + 2048 + 8
MAX_DELETE_SIZE = 64 * 1024
MIN_BLOCK_SIZE = 512  # 512B separation between indirect headers

MAX_VARIABLE_SECTIONS = 31
NUM_WORDS_VARIABLE_HEADER_RECORD = 3 # addr A, addr B, type

ROM_SECTIONS = ('PUF-ROM', )
RAM_SECTIONS = ('FIRMWARE', 'HOST', 'ENROLL_CERT')
MANDATORY_SECTIONS = ROM_SECTIONS + RAM_SECTIONS

DEFAULT_PADDING_LENGTH = "128"

config = {}
search_paths = []
fail_on_err = False
chip_type = None

# example: reserve( 0x1234, 'nrol') reserve(256 ,    ' rsr') etc...
RESERVE_REGEX = re.compile(r"reserve\(\s*(0x[0-9A-Fa-f]+|\d+)\s*,\s*'(.{4})'\s*\)")

def find_file_in_srcdirs(filename):
    global search_paths
    if filename:
        if os.path.isabs(filename) and os.path.isfile(filename):
            return filename

        pp = pprint.PrettyPrinter(indent=2)
        for dir in search_paths:
            file = os.path.join(dir, filename)
            if os.path.isfile(file):
                print('--> {} found in: {}'.format(filename,dir))
                return file
        print('Searching for {} in: {}'.format(filename,pp.pformat(search_paths)))
        print('--> {} not found'.format(filename))

    return None


def crc32(bytes):
    return binascii.crc32(bytes) & 0xffffffff

def pad_binary(binary, padding, minsize=0):
    """ pad to padding if necessary """
    if minsize > 0 and len(binary) < minsize:
        binary += bytearray(b'\xFF' * (minsize - len(binary)))

    overhang = len(binary) % padding

    if overhang:
        return binary + bytearray(b'\xFF' * (padding-overhang))

    return binary

def write_file(filename, content, tohex=False, tobyte=False):
    try:
        mode = "w" if tohex or tobyte else "wb"
        f = open(filename, mode)
    except:
        raise Exception("Cannot open file '%s' for write" % filename)
    if tohex:
        assert len(content)%4==0
        for pos in range(0, len(content), 4):
           f.write("%08X\n" % struct.unpack_from("<I", content, pos))
    elif tobyte:
        for pos in range(0, len(content)):
            f.write("%02X\n" % struct.unpack_from("B", content, pos))
    else:
        f.write(content)

def map_method_args(argmap, attrs):
    # set default empty arguments
    args = { v:None for v in argmap.values() }

    # map json parameters into function arguments
    args.update({ argmap[k]:v for k,v in attrs.items() \
                if k in argmap.keys() and len(str(attrs[k]))} )

    return args

def add_dice_location(args):
    dice_loc = kr.get_dice_loc(args['infile'], 0)
    if dice_loc == 0xFFFF_FFFF:
        return
    if (dice_loc & 0x3):
        raise Exception("DICE location is not 32 bit aligned")
    args['locations'].append(dice_loc >> 2)

def add_key_location(args, key_id):
    key_loc = kr.get_key_loc(args['infile'], key_id)
    if key_loc == 0xFFFF_FFFF:
        raise Exception("Could not find the key 0x%X" % key_id)
    if (key_loc & 0x3):
        raise Exception("Key location is not 32 bit aligned")
    args['locations'].append(key_loc >> 2)


def gen_fw_image(filename, attrs):
    global fail_on_err
    global chip_type
    argmap = {
        'cert':'certfile',
        'customer_cert':'customer_certfile',
        'fourcc':'ftype',
        'key':'sign_key',
        'key_index':'key_index',
        'keys_in_header' : 'keys_in_header',
        'source':'infile',
        'version':'version',
        'pad':'pad',
        'description':'description'
    }

    args = map_method_args(argmap, attrs)
    tmpfile = None

    if isinstance(args['infile'], list):
        tmpfile = tempfile.NamedTemporaryFile()
        for srcfile in args['infile']:
            with open(srcfile, 'rb') as f:
                tmpfile.write(f.read())
        args['infile'] = tmpfile.name
    else:
        args['infile'] = find_file_in_srcdirs(args['infile'])
    args['certfile'] = find_file_in_srcdirs(args['certfile'])
    args['customer_certfile'] = find_file_in_srcdirs(args['customer_certfile'])
    args['chip_type'] = chip_type
    args['locations'] = []

    if args['infile']:
        try:
            # add key locations if specified always first ...
            if args['keys_in_header']:
                #print("keys {}".format(args['keys_in_header']))
                for key in args['keys_in_header']:
                    #print("Key location {}".format(key))
                    add_key_location(args, int(key,0))

            # look for dice loc only in SBP executable images
            if args['ftype'] == 'pufr' or args['ftype'] == 'frmw':
                add_dice_location(args)

            fsi.image_gen(outfile=filename, **args)
        except Exception as e:
            raise RuntimeError("Failed to sign the image", e)
        if tmpfile:
            tmpfile.close()
        print("Generated signed image {} with the following parameters: {}".
              format(filename, args))
        return filename
    else:
        if attrs['source']:
            print("Skipping generation of {}, input {} not found!  parameters: {}".
                  format(filename, attrs['source'], args))

        else:
            print("Skipping generation of {}, no input specified".format(filename))
        if fail_on_err:
            raise RuntimeError("Failed to find input images")

    return None

def create_file(filename, section="signed_images"):
    global config

    if config.get(section):
        image = config[section].get(filename)
        if image:
            delete_after_sign = image.get('delete_after_sign')

            if delete_after_sign and os.path.exists(filename):
                return filename

            # process indirection to keybag
            if 'key_index' in image:
                # retrieve name of key from keybag specification
                key_bag_spec = config.get('key_bag_creation')
                if  not key_bag_spec:
                    raise Exception("key_index used for image {0}, but no or empty key_bag_creation section".
                                    format(filename))
                # use the first element in spec -- there's only one key bag now.
                key_list = next(iter(key_bag_spec.values()))
                image['key'] = key_list['keys'][image['key_index']]

            ret = gen_fw_image(filename, image)

            if delete_after_sign:
                os.remove(image['source'])

            return ret

    return None

def read_file_and_pad(filename, padding, optional, minsize, create):
    """read a file or a reserve() expression and return a padded binary """
    reserve_match = RESERVE_REGEX.search(str(filename))
    global config

    if reserve_match:
        return { 'type': bytearray(reserve_match.group(2).encode('ascii')),
                 'data': pad_binary(bytearray(b'\xFF' * int(reserve_match.group(1))), padding, minsize),
                 'input_size': 0 }

    if create:
        flash_file = create_file(filename)
    else:
        flash_file = find_file_in_srcdirs(filename)

    try:
        with open(flash_file, "rb") as f:
            binary = f.read()

    except:
        if optional:
            return { 'type': None,
                     'data': "",
                     'input_size': 0 }
        print("Required flash contents file {} not found\n".format(filename))
        raise

    return { 'type': binary[IMAGE_TYPE_OFFSET:IMAGE_TYPE_OFFSET+4],
             'data': pad_binary(bytearray(binary), padding, minsize),
             'input_size': len(binary) }


def get_a_and_b(section, padding, create, versions):
    """return the binaries and type for a section"""
    a_name = section['A']
    b_name = section['B']
    optional = section.get('optional', False)
    minsize = int(section.get('minsize', "0"),0)
    index = int(section.get('index', "0xffff"),0)

    if a_name:
        a_filename = a_name
        if versions:
            a_filename = f'{a_name}_{versions[0]}'
        a = read_file_and_pad(a_filename, padding, optional, minsize, create)
    if b_name:
        if b_name == a_name and not versions:
            b = a
        else:
            b_filename = b_name
            if versions:
                b_filename = f'{b_name}_{versions[1]}'
            b = read_file_and_pad(b_filename, padding, optional, minsize, create)
    else:
        b = { 'type': None,
              'data': [],
              'input_size': 0 }

    if a['type'] is not None and b['type'] is not None and a['type'] != b['type']:
        raise Exception("Images A and B for section %s have different types")

    if a['type'] is not None:
        section_type = a['type']
    elif b['type'] is not None:
        section_type = b['type']
    elif optional:
        return None
    else:
        raise Exception("Type must be specified (section %s)" % section)

    return {'a':a['data'],
            'a_input_size':a['input_size'],
            'b':b['data'],
            'b_input_size':b['input_size'],
            'type': section_type,
            'index': index}


def print_flash_map(bin_infos):
    print("Flash map:")
    for section in sorted(bin_infos, key=lambda x:bin_infos.get(x).get('index')):
        bin_info = bin_infos[section]
        print("Section {}: type = {}".format(section, bin_info['type']))
        print("\tImage A: 0x{:08x}-0x{:08x} (in: {} b, out: {} b)".format(bin_info['a_addr'],
                                        bin_info['a_addr'] + len(bin_info['a']),
                                        bin_info['a_input_size'],
                                        len(bin_info['a'])))
        print("\tImage B: 0x{:08x}-0x{:08x} (in: {} b, out: {} b)".format(bin_info['b_addr'],
                                        bin_info['b_addr'] + len(bin_info['b']),
                                        bin_info['b_input_size'],
                                        len(bin_info['b'])))


def generate_flash(bin_infos, total_size, padding):
    """generate the flash binary"""
    # fixed header with indexes and duplicate directories
    # aligned to MAX_DELETE_SIZE
    #
    # first page, 2 x directory block pointers and a CRC32 of those pointers
    # directory starts with a crc32 and then two PUF ROM pointers (a, b)
    # = 2 sections with 2 (a,b) addresses = 2 * 2
    # followed by a variable header with a crc:
    # variable header = (MAX_VARIABLE_SECTIONS + 1) with 2 (a,b) addresses+type
    # +1 : end of variable header = 2 words both 0xFFFF_FFFF

    # three delete sized blocks
    all_headers_length = 3 * MAX_DELETE_SIZE

    if padding > all_headers_length:
        all_headers_length = padding

    vhdr_words =  MAX_VARIABLE_SECTIONS * NUM_WORDS_VARIABLE_HEADER_RECORD
    vhdr_length = vhdr_words * 4

    curr_addr = all_headers_length

    # compute the addresses -- put ROM_SECTIONS first
    # address of A is the current address always.
    # address of B is different from address of A only if B is not empty
    # otherwise they are the same
    for section in sorted(bin_infos, key=lambda x:bin_infos.get(x).get('index')):
        if section in ROM_SECTIONS:
            bin_info = bin_infos[section]
            bin_info['a_addr'] = curr_addr

            curr_addr += len(bin_info['a'])
            if len(bin_info['b']):
                bin_info['b_addr'] = curr_addr
            else:
                bin_info['b_addr'] = bin_info['a_addr']

            curr_addr += len(bin_info['b'])

    for section in sorted(bin_infos, key=lambda x:bin_infos.get(x).get('index')):
        if section not in ROM_SECTIONS:
            bin_info = bin_infos[section]
            bin_info['a_addr'] = curr_addr
            curr_addr += len(bin_info['a'])
            if len(bin_info['b']):
                bin_info['b_addr'] = curr_addr
            else:
                bin_info['b_addr'] = bin_info['a_addr']

            curr_addr += len(bin_info['b'])


    # directory map
    dirptrs = struct.pack('<2I',
                          MAX_DELETE_SIZE,
                          2 * MAX_DELETE_SIZE)
    crc = struct.pack('<I', crc32(dirptrs))

    # pad out a single directory map to a nominal pad size
    dirmap = pad_binary(crc + dirptrs, MIN_BLOCK_SIZE)

    # duplicate the dirmap and pad out to the erase size
    dirmap_block = pad_binary(dirmap+dirmap, MAX_DELETE_SIZE)

    # fixed_header -- build and crc it
    dirhdr = bytearray()
    for section_name in ROM_SECTIONS:
        dirhdr.extend(struct.pack('<2I',
                        bin_infos[section_name]['a_addr'],
                        bin_infos[section_name]['b_addr']))

    crc = struct.pack('<I', crc32(dirhdr))

    directory_block = crc + dirhdr

    # variable header
    vhdr = bytearray()
    for section_name in RAM_SECTIONS:
        vhdr.extend(struct.pack('<2I',
                    bin_infos[section_name]['a_addr'],
                    bin_infos[section_name]['b_addr']))
        vhdr.extend(bytearray(bin_infos[section_name]['type']))

    # rest of variable header
    for section in bin_infos:
        if section not in MANDATORY_SECTIONS:
            bin_info = bin_infos[section]
            vhdr.extend(struct.pack('<2I',
                                 bin_info['a_addr'],
                                 bin_info['b_addr']))
            vhdr.extend(bin_info['type'])

    # pad the vhdr out for max sections -- doesn't include the crc itself
    vhdr = pad_binary(vhdr, vhdr_length)

    print("crc of variable header length %d" % len(vhdr))

    # crc the vhdr and construct the full block
    crc = struct.pack('<I', crc32(vhdr))
    directory_block += crc + vhdr

    # now pad the whole directory block
    directory_block = pad_binary(directory_block, MAX_DELETE_SIZE)


    # end of header + padding
    flash = dirmap_block + directory_block + directory_block
    if ((len(flash) % MAX_DELETE_SIZE) != 0):
        raise Exception("padding error assembling directory headers")

    if padding > MAX_DELETE_SIZE:
        flash = pad_binary(flash, padding)

    # data now
    # Add ROM_SECTIONS first to match the addresses
    for section in sorted(bin_infos, key=lambda x:bin_infos.get(x).get('index')):
        if section in ROM_SECTIONS:
            bin_info = bin_infos[section]
            flash += bin_info['a']
            if len(bin_info['b']):
                flash += bin_info['b']

    for section in sorted(bin_infos, key=lambda x:bin_infos.get(x).get('index')):
        if section not in ROM_SECTIONS:
            bin_info = bin_infos[section]
            flash += bin_info['a']
            if len(bin_info['b']):
                flash += bin_info['b']

    # pad to desired size
    if len(flash) > total_size:
        print("Overflowing specified space: 0x{:08x} > 0x{:08x}".format(len(flash), total_size))
        print_flash_map(bin_infos)
        raise Exception("Data doesn't fit into defined space")
    else:
        flash = pad_binary(flash, total_size)

    return flash

def from_binary_to_size( bin_info):
    ''' mapping function to replace binaries with their size '''
    # copy everything except the binaries
    mapped = {k:v for k,v in bin_info.items() if k not in ['a','b'] }
    # add size
    mapped['a_size'] = len(bin_info['a'])
    mapped['b_size'] = len(bin_info['b'])
    return mapped

def add_enrollment_certificate(binary, bin_infos, enroll_cert):
    ''' add the enrollment certificate to the flash image '''
    bin_info = bin_infos["ENROLL_CERT"]
    a_addr = bin_info['a_addr']
    b_addr = bin_info['b_addr']

    if a_addr == b_addr:
        new_binary = binary[0:a_addr] + enroll_cert + binary[a_addr + len(enroll_cert):]
    else:
        if a_addr < b_addr:
            low_addr = a_addr
            high_addr = b_addr
        else:
            low_addr = b_addr
            high_addr = a_addr

        new_binary = binary[0:low_addr] + enroll_cert + binary[a_addr + len(enroll_cert):b_addr] + \
                     enroll_cert + binary[b_addr + len(enroll_cert):]

    return new_binary

class FileJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, bytearray) or isinstance(o, bytes):
            return o.decode('ascii')
        return super().default(o)

def merge_configs(old, new, only_if_present=False):
    for k,v in new.items():
        if k in old and isinstance(old[k], dict) and isinstance(new[k], dict):
            merge_configs(old[k], new[k], only_if_present)
        else:
            if only_if_present and isinstance(new[k], dict):
                continue

            old[k] = new[k]

def override_field(config, field, value, only_if_empty=True):
    for k,v in config.items():
        if isinstance(v, dict):
            override_field(config[k], field, value, only_if_empty)
        elif k==field:
            if not (config.get(k) and only_if_empty):
                config[k] = value


def set_versions(value, only_if_empty=False):
    global config
    override_field(config, 'version', value, only_if_empty)

def set_description(value, only_if_empty=False):
    global config
    override_field(config, 'description', value, only_if_empty)

def main():
    parser = argparse.ArgumentParser()
    flash_content = None
    global config
    global search_paths
    global fail_on_err
    global chip_type

    parser.add_argument('config', nargs='+', help='Configuration file(s)')
    parser.add_argument('--config-type', default='json', choices={'json','ini'},
                        help="Configuration file format")
    parser.add_argument('--out-config', help="Write merged configuration file")
    parser.add_argument('--source-dir', action='append', default=[os.path.curdir],
                        help='Location of source files to be used (can be specified multiple times)')
    parser.add_argument('--action', default='all',
                        choices={'all', 'sign', 'flash', 'key_hashes', 'certificates', 'key_injection'},
                        help='Action to be performed on the input files')
    parser.add_argument('--force-version', action='append', default=[], type=int, help='Override firmware versions')
    parser.add_argument('--force-description', help='Override firmware description')
    parser.add_argument('--fail-on-error', action='store_true',
                        help='Always fail when encountering errors')
    parser.add_argument('--enroll-cert', metavar = 'FILE', help='Enrollment certificate')
    parser.add_argument('--chip', choices=['f1', 's1', 'f1d1', 's2', 'f2'], help='Target chip')

    args = parser.parse_args()

    search_paths = args.source_dir
    fail_on_err = args.fail_on_error
    chip_type = args.chip

    # read the configuration
    if args.config_type == 'ini':
        # convert legacy ini format to dict as generated from json
        config_ini = configparser.ConfigParser()

        # avoid converting keys to lowercase
        config_ini.optionxform = str
        config_ini.read(args.config)

        config['output_sections'] = {}

        for section in config_ini.sections():
            if section == 'All':
                config['output_format'] = dict(config_ini.items(section))
            else:
                config['output_sections'][section] = dict(config_ini.items(section))
                # ini-style files used 'optional' without value, so ensure
                # that it is set to True for new config format
                if 'optional' in config['output_sections'][section]:
                    config['output_sections'][section]['optional'] = True
    else:
        for config_file in args.config:
            if config_file == '-':
                x = json.load(sys.stdin)
                merge_configs(config, x)
            else:
                with open(config_file, 'r') as f:
                    merge_configs(config, json.load(f))

    if len(args.force_version) == 1:
        set_versions(args.force_version[0])

    if args.force_description:
        set_description(args.force_description)

    run(args.action, args.enroll_cert, force_versions=args.force_version if len(args.force_version) == 2 else None)

    if args.out_config:
        with open(args.out_config, "w") as f:
            json.dump(config, f, indent=4)

#TODO(mnowakowski) get rid of globals
def set_config(cfg):
    global config
    config = cfg

#TODO(mnowakowski) get rid of globals
def set_search_paths(paths):
    global search_paths
    search_paths = paths

def set_chip_type(chip):
    global chip_type
    chip_type = chip

def run(arg_action, arg_enroll_cert = None, *args, **kwargs):
    global config
    global search_paths

    wanted = lambda action : arg_action in ['all', action]
    flash_content = None

    new_entries = {}
    delete_entries = []
    versions = kwargs.get('force_versions', None)

    for k,v in config['signed_images'].items():
        if v.get('description','').startswith('@file:'):
            try:
                with open(find_file_in_srcdirs(v['description'][len('@file:'):]), 'r') as f:
                    v['description'] = f.readline()
            except:
                raise Exception("Could not find file {0}".format(v['description'][len('@file:'):]))

        if v.get('source','').startswith('@file:'):
            try:
                with open(find_file_in_srcdirs(v['source'][len('@file:'):]), 'r') as f:
                    files = json.load(f)
                    for vv in files.values():
                        fname = vv.get('target')
                        if not fname:
                            fname = '{}.bin'.format(vv['filename'])
                        new_v = copy.deepcopy(v)
                        new_v['source'] = vv['filename']
                        new_v['image_type'] = vv.get('image_type', "")
                        new_entries[fname] = new_v
            except:
                print("Skipping generation of {}, input file {} not found".format(
                    k, v['source'][len('@file:'):]))

            delete_entries.append(k)

    # python3 doesn't allow changing dict size during iteration
    # so perform any updates after the loop
    for k in delete_entries:
        config['signed_images'].pop(k)

    config['signed_images'].update(new_entries)

    if versions:
        assert len(versions) == 2
        # Create a new replacement dictionary that will contain two copies
        # of each of the images so that they can be signed with different
        # firmware versions
        r = {}
        for k,v in config['signed_images'].items():
            for id, ver in enumerate(versions):
                new_v = copy.deepcopy(v)
                new_v['version'] = ver
                r[f'{k}_{ver}'] = new_v
        config['signed_images'] = r


    if config.get('output_format'):
        total_size = int(config['output_format']['size'], 0)
        output = config['output_format']['output']
        padding = int(config['output_format']['page'], 0)

    # do not use wanted() here, as this is an action only
    # executed when requested explicitly
    if arg_action == 'sources':
        for outfile, v in config['signed_images'].items():
            infile = find_file_in_srcdirs(v['source'])

            if infile:
                shutil.copy2(infile, v['source'])
            else:
                src = config.get('key_injection')
                if src:
                    src = src.get(v['source'])
                if src and src['source']:
                    infile = find_file_in_srcdirs(src['source'])
                    if infile:
                        shutil.copy2(infile, src['source'])

    # Generate keys (if required)
    if wanted('key_hashes') and 'key_hashes' in config:
        for k,v in config['key_hashes'].items():
            fsi.export_pub_key_hash(k, chip_type, v['name'])

    # Generate certificates (if required)
    if wanted('certificates') and 'certificates' in config:
        for k,v in config['certificates'].items():
            file = find_file_in_srcdirs(k)
            if file:
                print("File {} already exists and will not be generated".
                      format(file))
            else:
                argmap = {
                    'public':'cert_key',
                    'security_group':'security_group'
                 }
                cert_args = map_method_args(argmap, v)
                fsi.get_cert(outfile=k,
                             chip_type=chip_type,
                             **cert_args)

    if wanted('key_injection') and config.get('key_injection'):
        keep_outfile = kwargs.get("keep_output", False)
        for outfile, v in config['key_injection'].items():
            if not (os.path.exists(outfile) and keep_outfile):
                infile = find_file_in_srcdirs(v['source'])
                shutil.copy2(infile, outfile)
            for key in v['keys']:
                kr.update_file(outfile, key['id'], key=key['name'])

    if wanted('key_injection') and config.get('key_bag_creation'):
        # keybag is always created from scratch....
        for outfile, v in config['key_bag_creation'].items():
            kbc.create(outfile, v['keys'])

    if wanted('flash') and config.get('output_format'):
        bin_infos = dict()
        if len(config.get('output_sections', {})) == 0:
            # only All section -> empty file
            flash_content = pad_binary(b'\xFF', total_size)
        elif len(config.get('output_sections',{})) > 1 + MAX_VARIABLE_SECTIONS:
            raise Exception("Too many sections: {0}, max is {1}".
                                format(len(config.sections()), 1 + MAX_VARIABLE_SECTIONS))
        else:
            for k,v in config['output_sections'].items():
                bin_info = get_a_and_b(v, padding, arg_action == 'all', versions)
                # bin_info can be None if optional section and files
                # are not there -> no entry
                if bin_info is not None:
                    bin_infos[k] = bin_info

            # file must have at least PUF-ROM, START-CERT, FIRMWARE and HOST section
            if not all(ss in bin_infos for ss in MANDATORY_SECTIONS):
                raise Exception('Configuration file: mandatory section(s) missing')
            flash_content = generate_flash(bin_infos, total_size, padding)

        # enrollment certificate argument?
        enroll_cert = None

        if arg_enroll_cert:
            try:
                with open(arg_enroll_cert, "rb") as f:
                    enroll_cert = f.read()
            except:
                enroll_cert = None

        if enroll_cert:
            flash_content = add_enrollment_certificate(flash_content,
                                                       bin_infos,
                                                       enroll_cert)

        print_flash_map(bin_infos)

        if versions:
            # Create a new replacement dictionary that will contain two copies
            # of each of the images so that they can be signed with different
            # firmware versions
            r = {}
            for k,v in config['signed_meta_images'].items():
                for id, ver in enumerate(versions):
                    new_v = copy.deepcopy(v)
                    new_v['version'] = ver
                    new_v['source'] = [f'{s}_{ver}' for s in v['source']]
                    r[f'{k}_{ver}'] = new_v
            config['signed_meta_images'] = r

        for file in config.get("signed_meta_images", {}):
            create_file(file, "signed_meta_images")

    # Write output
    if flash_content:
        write_file(output+'.bin', flash_content)
        write_file(output+'.hex', flash_content, tohex=True)
        write_file(output+'.byte', flash_content, tobyte=True)
    else:
        if wanted('sign'):
            for file in config.get("signed_images", {}):
                create_file(file)
            for file in config.get("signed_meta_images", {}):
                create_file(file, "signed_meta_images")

    # For non-empty flash, generate map file
    if wanted('flash') and len(config.get('output_sections', {})) > 0:
        # Write directory file used by board_init.py for QSPI
        # = dictionary without the binary and with the size
        flash_map = {k: from_binary_to_size(v) for k,v in bin_infos.items() }

        with open(output + '.map', 'w') as f:
            json.dump(flash_map, f, indent=4, cls=FileJsonEncoder)


if __name__=="__main__":
    main()
