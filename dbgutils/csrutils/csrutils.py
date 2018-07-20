#!/usr/bin/env python
import argparse, json
import string, os
import collections
import binascii
import socket
import jsocket
import time
import logging
import traceback
import urllib
import requests
import tarfile
from array import array

logger = logging.getLogger("csrutils")
logger.setLevel(logging.INFO)

class constants(object):
    SERVER_TCP_PORT = 55667
    WORD_SIZE_BITS = 64
    MAX_WORD_VALUE = 0xFFFFFFFFFFFFFFFF
    CSR_CFG_DIR = "FunSDK/config/csr/"
    TMP_DIR = '/tmp'
    CSR_METADATA_FILE = 'csr_metadata.json'

# Opens tcp connection with remote server
def i2c_remote_connect(ip_address):
    s = jsocket.JsonClient(address = ip_address,
			   port = constants.SERVER_TCP_PORT)
    if s is None:
        print("Failed to connect to i2c server {0}".format(ip_address))
        return None
    s.connect()
    time.sleep(0.5)
    s.send_obj({"cmd": "CONNECT",
                "args": None})
    read_obj = s.read_obj()
    status = read_obj.get("STATUS", None)
    logger.info("Remote connect status: {0}".format(status))
    if status is not None and status[0] == True:
        return s
    else:
        s.close()
        return None

# Sends peek request to server, get the response and returns the read data
def i2c_remote_peek(s, csr_addr, csr_width_words):
    logger.debug(("s: {0} csr_addr:{1} csr_width_words:{2}").format(s, csr_addr,
                                                             csr_width_words))
    if s is None or csr_addr is None or csr_width_words is None \
            or csr_addr == 0 or csr_width_words < 1:
        print("Invalid peek arguments!")
        return None
    csr_peek_args = dict()
    csr_peek_args["csr_addr"] = csr_addr
    csr_peek_args["csr_width"] = csr_width_words
    s.send_obj({"cmd": "CSR_PEEK",
                "args": csr_peek_args})
    msg = s.read_obj()
    logger.debug(msg)
    status = msg.get("STATUS", None)
    if status[0] == True:
        word_array = msg.get("DATA", None)
        return word_array
    else:
        print("I2C peek over socket failed!")
        return None

# Sends poke request to server, get the response
def i2c_remote_poke(s, csr_addr, csr_width_words, word_array):
    logger.debug(("csr_addr:{0} csr_width_words:{1}"
        " word_array{2}").format(csr_addr,
            csr_width_words, word_array))
    if s is None:
        print 'i2c server is not connected!'
        return
    if csr_addr is None or csr_width_words is None \
            or word_array is None or csr_addr == 0 \
            or csr_width_words < 1:
        logger.info(("csr_addr:{0} csr_width_words:{1}"
           " word_array{2}").format(csr_addr,
               csr_width_words, word_array))
        print("Invalid poke arguments!")
        return False

    csr_poke_args = dict()
    csr_poke_args["csr_addr"] = csr_addr
    csr_poke_args["csr_width"] = csr_width_words
    csr_poke_args["csr_val"] = word_array
    s.send_obj({"cmd": "CSR_POKE",
                "args": csr_poke_args})
    msg = s.read_obj()
    status = msg.get("STATUS", None)
    if status[0] == True:
        logger.debug("poke success!")
        return True
    else:
        print("Error! poke failed!: {0}".format(status[1]))
        return False

# Disconnects remote i2c connection and socket connection to remote server
def i2c_remote_disconnect(s):
    if s is None:
        print("Not connected to server")
        return
    s.send_obj({"cmd": "DISCONNECT",
                "args": None })
    read_obj = s.read_obj()
    status = read_obj.get("STATUS", None)
    if status[0] == True:
        logger.info("Success! {0}".format(status[1]))
        s.close()
        return True
    else:
        logger.error("Error! {0}".format(status[1]))
        s.close()
        return False

# csr peek handler for command line interface
def csr_peek(args):
    global i2c_server_socket
    input_args = csr_get_peek_args(args)
    csr_name = input_args.get("csr_name", None)
    csr_inst = input_args.get("csr_inst", None)
    csr_entry = input_args.get("csr_entry", None)
    ring_name = input_args.get("ring_name", None)
    ring_inst = input_args.get("ring_inst", None)
    anode_name = input_args.get("anode_name", None)
    anode_inst = input_args.get("anode_inst", None)
    anode_path = input_args.get("anode_path", None)
    field_list = input_args.get("field_list", None)

    csr_data = csr_get_metadata(csr_name, csr_inst=csr_inst, csr_entry=csr_entry,
            ring_name=ring_name, ring_inst=ring_inst, anode_name=anode_name,
            anode_inst=anode_inst, anode_path=anode_path)

    if csr_data is None:
        print("Error! Failed to get metadata for csr:{} !!!".format(csr_name))
        return

    csr_addr = csr_get_addr(csr_data, anode_inst=anode_inst,
                            csr_inst=csr_inst, csr_entry=csr_entry)
    if csr_addr is None:
        print("Error get csr address!!!")
        return
    logger.debug("csr address: {0}".format(hex(csr_addr)))

    csr_width_bytes = csr_get_width_bytes(csr_data)
    csr_width_words = csr_width_bytes >> 3
    word_array = None
    if i2c_server_socket is not None:
        word_array = i2c_remote_peek(i2c_server_socket, csr_addr, csr_width_words)
        if word_array is None or not word_array:
            print("Error in csr i2c peek!!!")
            return None
        logger.debug("Peeked value: {0}".format(hex_word_dump(word_array)))
        print("I2C peek is success!")
        csr_show(csr_data, word_array, field_list)
    else:
        print("Error! Not connected to i2c server!")

# csr poke handler for commandline interface
def csr_poke(args):
    input_args = csr_get_poke_args(args)
    csr_name = input_args.get("csr_name", None)
    csr_inst = input_args.get("csr_inst", None)
    csr_entry = input_args.get("csr_entry", None)
    ring_name = input_args.get("ring_name", None)
    ring_inst = input_args.get("ring_inst", None)
    anode_name = input_args.get("anode_name", None)
    anode_inst = input_args.get("anode_inst", None)
    anode_path = input_args.get("anode_path", None)
    field_list = input_args.get("field_list", None)
    raw_value = input_args.get("raw_value", None)

    csr_data = csr_get_metadata(csr_name, csr_inst=csr_inst, csr_entry=csr_entry,
            ring_name=ring_name, ring_inst=ring_inst, anode_name=anode_name,
            anode_inst=anode_inst, anode_path=anode_path)

    if csr_data is None:
        print("Error! Failed to get metadata for csr:{} !!!".format(csr_name))
        return

    csr_addr = csr_get_addr(csr_data, anode_inst=anode_inst,
                            csr_inst=csr_inst, csr_entry=csr_entry)
    if csr_addr is None:
        print("Error get csr address!!!")
        return

    csr_width_bytes = csr_get_width_bytes(csr_data)
    csr_width_words = csr_width_bytes >> 3

    if i2c_server_socket is None:
        print("Error! Not connected to i2c server!")
        return
    if raw_value is not None:
        word_array = list()
        for word in raw_value:
            value = str_to_int(word)
            if value is None:
                print(('Invalid field input value: "{0}". Must be positive'
                       'integer or hexadecimal').format(word))
                return None
            word_array.append(value)

        if len(word_array) != csr_width_words:
            print(("Number of raw value words should match csr width.\n"
                  " csr: {0}.\nExpected {1} word(s) but given {2}.").format(
                  json_obj_pretty(csr_data), csr_width_words, len(word_array)))
            return None
        print(hex_word_dump(word_array))
    elif field_list is not None:
        word_array = i2c_remote_peek(i2c_server_socket, csr_addr, csr_width_words)
        if word_array is None or not word_array:
            print("csr poke failed!. i2c remote peek error while doing read/modify/write!!!")
            return None

        logger.debug("Peeked value: {0}".format(hex_word_dump(word_array)))
        valid_field_list = csr_get_valid_field_list(csr_data)
        for field in field_list:
            field_name = field[0]
            if field_name not in valid_field_list:
                print("Invalid field name: {0}."
                      " Valid fields are: {1}".format(field_name,
                                                      valid_field_list.keys()))
                return None
            str_word_array = field[1:]
            field_word_array = list()
            for word in str_word_array:
                value = str_to_int(word)
                if value is None:
                    print('Invalid field input value: "{0}". Must be positive'
                          ' integer or hexadecimal'.format(word))
                    return None
                field_word_array.append(value)

            field_obj = valid_field_list.get(field_name, None)
            field_width = field_obj.get("fld_width", None)
            field_width_words = (field_width + 63) / 64
            field_offset = field_obj.get("fld_offset", None)
            if not field_width_words:
                sys.exit(1)
            if len(field_word_array) > field_width_words:
                print(("Number of field value words should match the length"
                       " for the field. csr:\n{0}.\nExpected {1} words"
                       " but given {2}.").format(json_obj_pretty(csr_data),
                       field_width_words, len(field_word_array)))
                return None
            csr_set_field(field_offset, field_width, word_array, field_word_array)
            logger.debug(field_name)
            logger.debug(field_word_array)
            logger.debug(hex_word_dump(word_array))
    else:
        print("Invalid input values! poke should"
              " have either field list with values or raw values")
        return None
    status = i2c_remote_poke(i2c_server_socket, csr_addr,
                             csr_width_words, word_array)
    if status == True:
        print("Poke Success!")
    else:
        print("Error! poke failed!")
        return


# csr list handler for commandline interface
def csr_list(args):
    csr_name = args.csr[0]
    if not csr_name:
        print("csr name is empty! Provide valid csr name!")
        return
    ring_name = args.ring[0] if args.ring else None
    anode_name = args.anode[0] if args.anode else None

    csr_list = csr_metadata().get_csr_def(csr_name, rn_class=ring_name, an=anode_name)
    if csr_list is None:
        print("csr: {} doesnot exist in database!.".format(csr_name))
        return
    print("Matching csr entries for csr:{0}".format(csr_name))
    print(json_obj_pretty(csr_list))

#import pdb
# Find csr medata matching an address
def csr_find_addr_metadata(caddr):
    print hex(caddr)
    csr_dict =  csr_metadata().get_metadata()
    if not csr_dict:
        print "Can't get csr metadata!"
        return None
    print "Done Loading"
    for k, v in csr_dict.iteritems():
        if k == 'psw_sch_qsch_cfg_extrabw_sp_queues_fp':
            pass
            #pdb.set_trace()
        for csr_data in v:
            address = caddr
            anode_addr = csr_data.get("an_addr", None)
            if anode_addr is None:
                print("Invalid csr metadata! anode_addr is missing in metadata!")
                sys.exit(1)
            anode_addr = int(anode_addr, 16)
            start_anode_addr = anode_addr
            anode_inst_cnt = csr_data.get("an_inst_cnt", None)
            if anode_inst_cnt is None:
                print("Invalid csr metadata! an_inst_cnt is missing in metadata!")
                sys.exit(1)

            anode_skip_addr = 0
            anode_inst = 0
            if anode_inst_cnt > 1:
                anode_skip_addr = csr_data.get("an_skip_addr", None)
                if anode_skip_addr is None:
                    print("Invalid csr metadata! an_skip_addr is missing in metadata!")
                    sys.exit(1)
                anode_skip_addr = int(anode_skip_addr, 16)
                end_anode_addr = start_anode_addr + (anode_skip_addr *
                                                     anode_inst_cnt);

                if address < start_anode_addr or address >= end_anode_addr:
                    continue

                x = address - start_anode_addr
                anode_inst = x / anode_skip_addr
                address = address - (anode_inst * anode_skip_addr)

            csr_addr = csr_data.get("csr_addr", None)
            if csr_addr is None:
                print("Invalid csr metadata! csr_addr is missing in metadata!")
                sys.exit(1)
            csr_addr = int(csr_addr, 16)

            csr_inst_start_addr = csr_addr
            csr_width = csr_data.get("csr_width", None)
            if csr_width is None:
                print("Invalid csr metadata! csr_width is missing in metadata!")
                sys.exit(1)
            csr_width_bytes = csr_width >> 0x3

            csr_n_entries = csr_data.get("csr_n_entries", None)
            if csr_n_entries is None:
                print("Invalid csr metadata! csr_n_entries is missing in metadata!")
                sys.exit(1)
            csr_inst_skip_addr = csr_width_bytes * csr_n_entries

            csr_inst_count = csr_data.get("csr_count", None)
            if csr_inst_count is None:
                print("Invalid csr metadata! csr_inst_count is missing in metadata!")
                sys.exit(1)

            address -= start_anode_addr
            csr_inst_end_addr = csr_inst_start_addr
            if csr_inst_count > 0:
                csr_inst_end_addr += csr_inst_skip_addr * csr_inst_count

            if address < csr_inst_start_addr or address >= csr_inst_end_addr:
                continue

            address -= csr_inst_start_addr
            csr_inst = address / csr_inst_skip_addr
            address -= csr_inst * csr_inst_skip_addr

            csr_start_addr = address
            csr_end_addr = csr_start_addr
            if csr_n_entries > 0:
                csr_end_addr = csr_start_addr + (csr_width_bytes * csr_n_entries)

            if address < csr_start_addr or address >= csr_end_addr:
                continue
            csr_index = address / csr_width_bytes

            print json_obj_pretty({k:csr_data})
            print ("csr: {0} anode_inst: {1} csr_inst: {2} csr_index:"
                " {3}").format(k, anode_inst, csr_inst, csr_index)
            return ({k:csr_data, "anode_inst": anode_inst,
                    "csr_inst": csr_inst, "csr_index": csr_index})
    print "Invalid address: {0}. No valid csr found!".format(hex(caddr))
    return None

# csr find handler for commandline interface.
# Returnds names of all the csrs which contain input substring
def csr_find(args):
    print args

    csr_name = args.substring[0] if args.substring else None
    csr_address = args.csr_address[0] if args.csr_address else None

    if csr_name:
        csr_list = csr_metadata().get_csr_list()
        matched_csr_list = list()
        for x in csr_list:
            if csr_name in x:
                matched_csr_list.append(x)
        if not matched_csr_list:
            print('There are no csrs in database matching "{0}"!'.format(csr_name))
            return
        print('Matching csr entries for "{0}"'.format(csr_name))
        print(json_obj_pretty(matched_csr_list))
    elif csr_address:
        address = str_to_int(csr_address)
        if address and address > 0:
            csr_find_addr_metadata(address)
        else:
            print "Invalid address!"
            return
    else:
        print('Invalid argument! args:{0}'.format(args))
        return

def csr_metadata_dochub():
    url = 'http://dochub.fungible.local/doc/jenkins/funsdk/latest/Linux/csr-cfg.tgz'
    file_tmp = urllib.urlretrieve(url, filename=None)[0]
    base_name = os.path.basename(url)
    file_name, file_extension = os.path.splitext(base_name)
    tar = tarfile.open(file_tmp)
    tar.extract('./'+ constants.CSR_CFG_DIR + constants.CSR_METADATA_FILE, '/tmp')
    return True

def csr_load_metadata(args):
    if args.default:
        status = csr_metadata().load_metadata_from_dochub()
        if not status:
            print 'Failed to load metadata from dochub!'
            return
    elif args.sdk_root_dir:
        sdk_root_dir = args.sdk_root_dir[0]
        sdk_root_dir = os.path.abspath(sdk_root_dir)
        if not os.path.exists(sdk_root_dir):
            print  'SDK root dir: "{}": does not exist!'.format(sdk_root_dir)
            return
        status = csr_metadata().load_metadata_from_sdk(sdk_root_dir)
        if not status:
            print 'Failed to load metadata from sdk dir: {}!'.format(sdk_root_dir)
            return
    else:
        print "Invalid metadta arguments!"
        return
    return
def csr_replay(args):
    replay_file = args.replay_file[0]
    if not os.path.isabs(replay_file):
        replay_file = os.path.join(os.getcwd(), replay_file)
    if not os.path.isfile(replay_file):
        print 'Path: "{0}" is not a regular file!'.format(replay_file)
        return
    with open(replay_file) as fp:
        line = fp.readline()
        cnt = 1
        while line:
            line = line.rstrip()
            csr_tokens = line.split(':')
            if len(csr_tokens) < 4:
                print 'Skipping line: "{0}"'.format(line)
                line = fp.readline()
                continue
            print("Line {}: {}".format(cnt, line.strip()))
            if csr_tokens[0] != 'CSRWR':
                line = fp.readline()
                continue
            for count, token in enumerate(csr_tokens[1:], start=1):
                csr_tokens[count] =  str_to_int(csr_tokens[count])
                if csr_tokens[count] is None:
                    print 'Invalid csr replay data!: "{0}"'.format(line)
                    return

            csr_address = csr_tokens[1]
            csr_width_words = csr_tokens[2]
            if not csr_width_words:
                print 'Invalid csr width in input data: "{0}"'.format(line)
                return
            csr_width_words = (csr_width_words + 63) / 64
            csr_val_words = csr_tokens[3:]
            if csr_width_words != len(csr_val_words):
                print 'Mismatch in csr width and value. "{0}"'.format(line)
                return
            if i2c_server_socket is None:
                print 'i2c server is not connected!'
                return
            logger.debug('csr_address: {0} csr_width_words: {1}'
                    'word_array:{2}'.format(csr_address,
                        csr_width_words, csr_val_words))
            status = i2c_remote_poke(i2c_server_socket, csr_address,
                   csr_width_words, csr_val_words)
            if status == True:
                print('Succesfully replayed "{0}"!'.format(line))
                cnt += 1
            else:
                print('Replay failed! "{0}"! Replay stopped!'.format(line))
                return
            line = fp.readline()
    print('Succesfully replayed {0} CSRs!'.format(cnt))

# csr connect handler for commandline interface.
# Connects remote server
i2c_server_socket = None
def server_connect(args):
    global i2c_server_socket
    ip_address = args.ip_addr[0]
    try:
        socket.inet_aton(ip_address)
        # legal
    except socket.error:
        print("Invalid ip address!")
        return
    if i2c_server_socket is not None:
        try:
            i2c_remote_disconnect(i2c_server_socket)
        except Exception as e:
            logging.error(traceback.format_exc())
            logger.info('Still proceeding with connect..!')
        i2c_server_socket = None

    s = i2c_remote_connect(ip_address)
    if s is not None:
        print("Server connection Success!")
        i2c_server_socket = s
    else:
        print("Server connection failed!")


# csr disconnect handler for commandline interface.
# Disconnects from remote server
def server_disconnect(args):
    global i2c_server_socket
    if i2c_server_socket is None:
        print("Not connected to server")
        return

    status = i2c_remote_disconnect(i2c_server_socket)
    i2c_server_socket = None
    print("Server disconnected!");
    return

# Read peek input args
def csr_get_peek_args(args):
    input_args = dict()
    input_args["csr_name"] = args.csr[0]
    input_args["csr_inst"] = int(args.csr_inst[0], 10) if args.csr_inst else None
    input_args["csr_entry"] = int(args.csr_entry[0], 10) if args.csr_entry else None
    input_args["ring_name"] = args.ring[0] if args.ring else None
    input_args["ring_inst"] = None
    if args.ring and len(args.ring) > 1:
        input_args["ring_inst"] = int(args.ring[1], 10)
    input_args["anode_name"] = args.anode[0] if args.anode else None
    input_args["anode_inst"] = None
    if args.anode and len(args.anode) > 1:
        input_args["anode_inst"] = int(args.anode[1], 10)
    input_args["anode_path"] = args.an_path[0] if args.an_path else None
    input_args["field_list"] = args.fields

    return input_args

# Read poke input args
def csr_get_poke_args(args):
    input_args = dict()
    input_args["csr_name"] = args.csr[0]
    input_args["csr_inst"] = int(args.csr_inst[0], 10) if args.csr_inst else None
    input_args["csr_entry"] = int(args.csr_entry[0], 10) if args.csr_entry else None
    input_args["ring_name"] = args.ring[0] if args.ring else None
    input_args["ring_inst"] = None
    if args.ring and len(args.ring) > 1:
        input_args["ring_inst"] = int(args.ring[1], 10)
    input_args["anode_name"] = args.anode[0] if args.anode else None
    input_args["anode_inst"] = None
    if args.anode and len(args.anode) > 1:
        input_args["anode_inst"] = int(args.anode[1], 10)
    input_args["anode_path"] = args.an_path[0] if args.an_path else None
    input_args["field_list"] = args.fields
    input_args["raw_value"] = args.raw_value

    return input_args


# Returns csr address
def csr_get_addr(csr_data, anode_inst=None, csr_inst=None, csr_entry=None):
    anode_addr = csr_data.get("an_addr", None)
    if anode_addr is None:
        print("Invalid csr metadata! anode_addr is missing in metadata!")
        sys.exit(1)
    anode_addr = int(anode_addr, 16)
    anode_inst_cnt = csr_data.get("an_inst_cnt", None)
    if anode_inst_cnt is None:
        print("Invalid csr metadata! an_inst_cnt is missing in metadata!")
        sys.exit(1)

    if anode_inst_cnt > 1:
        if anode_inst is None:
            print("Expetced anode_inst argument!")
            return None

        if anode_inst < 0 or anode_inst >= anode_inst_cnt:
            print("Invalid anode_inst: {}!".format(anode_inst))
            return None

        anode_skip_addr = csr_data.get("an_skip_addr", None)
        if anode_skip_addr is None:
            print("Invalid csr metadata! an_skip_addr is missing in metadata!")
            sys.exit(1)

        anode_addr = int(anode_skip_addr, 16) * anode_inst;

    csr_addr = csr_data.get("csr_addr", None)
    if csr_addr is None:
        print("Invalid csr metadata! csr_addr is missing in metadata!")
        sys.exit(1)

    csr_addr = int(csr_addr, 16)
    csr_width = csr_data.get("csr_width", None)
    if csr_width is None:
        print("Invalid csr metadata! csr_width is missing in metadata!")
        sys.exit(1)

    csr_width_bytes = csr_width >> 0x3

    csr_n_entries = csr_data.get("csr_n_entries", None)
    if csr_n_entries is None:
        print("Invalid csr metadata! csr_n_entries is missing in metadata!")
        sys.exit(1)

    if csr_n_entries > 1:
        if csr_entry is None:
            print("Expetced csr_entry argument!")
            return None

        if csr_entry < 0 or csr_entry >= csr_n_entries:
            print("Invalid csr_entry: {}!".format(csr_entry))
            return None
        csr_addr += csr_width_bytes * csr_entry;

    csr_inst_count = csr_data.get("csr_count", None)
    if csr_inst_count is None:
        print("Invalid csr metadata! csr_inst_count is missing in metadata!")
        sys.exit(1)

    if csr_inst_count > 1:
        if csr_inst is None:
            print("Expetced csr_inst argument!")
            return None

        if csr_inst < 0 or csr_inst >= csr_inst_count:
            print("Invalid csr_inst: {}!".format(csr_inst))
            return None
        csr_addr += csr_width_bytes * csr_n_entries * csr_inst

    return (anode_addr + csr_addr)

# Returns width of a csr in bytes
def csr_get_width_bytes(csr_data):
    csr_width = csr_data.get("csr_width", None)
    if csr_width is None:
        print("Invalid csr metadata! csr_width is missing in metadata!")
        sys.exit(1)

    csr_width_bytes = csr_width >> 0x3

    return csr_width_bytes

# Reads the field from input word array and returns field value as word array
def csr_get_field(fld_pos, fld_size, word_array):
    constants.WORD_SIZE_BITS = 64
    reg_padded_size = len(word_array) * constants.WORD_SIZE_BITS
    if not (reg_padded_size >= fld_size + fld_pos):
        print(("Invalid arguments! fld_pos: {0} + fld_size: {1} exceeds"
               " csr word array length: {2}").format(fld_pos, fld_size,
                                len(word_array) * constants.WORD_SIZE_BITS))
        sys.exit(1)

    if not fld_size > 0:
        print(("Invalid argument! fld_size: {0}"
               " should non-zero positive number").format(fld_size))
        sys.exit(1)

    out_idx = 0
    rem_size = fld_size

    # compute the last word of the output buffer because big endian
    out_idx = (fld_size - 1) / constants.WORD_SIZE_BITS
    logger.debug("first output word: {0}".format(out_idx))

    fld_size_words = (fld_size + (constants.WORD_SIZE_BITS - 1)) / constants.WORD_SIZE_BITS
    fld_word_array = [0x0] * fld_size_words

    # count up bits from fld_pos
    while rem_size > 0:
        # clear the output word
        if not (out_idx >= 0):
            sys.exit(1)
        fld_word_array[out_idx] = 0

        # find the input word for the lowest significant bit
        if not ((reg_padded_size - fld_pos - fld_size + rem_size) > 0):
            sys.exit(1)
        in_idx = (reg_padded_size - fld_pos - fld_size + rem_size - 1) / constants.WORD_SIZE_BITS

        # calculate the base bit position in this word
        in_pos = fld_pos % constants.WORD_SIZE_BITS

        # trim the size for this input word
        in_size = rem_size
        read_upper = False
        if (in_size + in_pos > constants.WORD_SIZE_BITS):
            in_size = constants.WORD_SIZE_BITS - in_pos
            read_upper = True

        # calculate a mask
        if (in_size == constants.WORD_SIZE_BITS):
            mask = constants.MAX_WORD_VALUE
        else:
            mask = (0x1 << in_size) - 1

        logger.debug("in_idx: {0}".format(in_idx))
        logger.debug("mask: {0}".format(hex(mask)))
        logger.debug("fld_size: {0} -> {1}".format(fld_size, in_size))

        # copy in the first part of the word
        fld_word_array[out_idx] |= (word_array[in_idx] >> in_pos) & mask

        # determine if we need to read part of the next word
        if (read_upper):
            # need to read the remaining bits in this input word
            if (constants.WORD_SIZE_BITS < rem_size):
                in_size_hi = constants.WORD_SIZE_BITS - in_size
            else:
                in_size_hi = rem_size - in_size
            if not (in_size_hi < constants.WORD_SIZE_BITS): # can't be constants.WORD_SIZE_BITS, would be read above
                sys.exit(1)
            # construct the mask
            mask = (0x1 << in_size_hi) - 1

            # or in the value
            if not ((in_idx - 1) >= 0):
                sys.exit(1)
            fld_word_array[out_idx] |= (word_array[in_idx-1] & mask) << in_size
        else:
            in_size_hi = 0

        logger.debug(("rem_size: {0}, in_size: {1}, in_size_hi: {2}").format(rem_size,
                in_size, in_size_hi, (rem_size -  in_size + in_size_hi)))

        # next output word
        out_idx -= 1
        rem_size -= in_size + in_size_hi
    return fld_word_array

def csr_set_field(fld_pos, fld_size, csr_word_array, fld_word_array):
    constants.WORD_SIZE_BITS = 64
    reg_padded_size = len(csr_word_array) * constants.WORD_SIZE_BITS

    if not (reg_padded_size >= fld_size + fld_pos):
        print(("Invalid arguments! fld_pos: {0} + fld_size: {1} exceeds"
               "csr word array length: {2}").format(fld_pos, fld_size,
                len(csr_word_array) * constants.WORD_SIZE_BITS))
        sys.exit(1)

    if not fld_size > 0:
        print(("Invalid argument! fld_size: {0}"
               " should non-zero positive number").format(fld_size))
        sys.exit(1)

    rem_size = fld_size
    in_idx = (fld_size - 1) / constants.WORD_SIZE_BITS
    while (rem_size > 0):
        # find the LSB word on the output register
        if not ((reg_padded_size - fld_pos - fld_size + rem_size) > 0):
            sys.exit(1)
        out_idx = (reg_padded_size - fld_pos - fld_size + rem_size - 1) / constants.WORD_SIZE_BITS

        # calculate the base bit position in this word
        out_pos = fld_pos % constants.WORD_SIZE_BITS

        # trim the size for this input word
        out_size = rem_size
        write_upper = False
        if (out_size + out_pos > constants.WORD_SIZE_BITS):
            out_size = constants.WORD_SIZE_BITS - out_pos
            write_upper = True

        # calculate a mask
        if (out_size == constants.WORD_SIZE_BITS):
            mask = constants.MAX_WORD_VALUE
        else:
            mask = (0x1 << out_size) - 1

        logger.debug("out_idx: {0}, in_idx: {1}".format(out_idx, in_idx))
        logger.debug("mask: {0}".format(mask))
        logger.debug("fld_size: {0} -> {1}".format(fld_size, out_size))

        # copy in the first part of the word, masking out the rest
        csr_word_array[out_idx] &= ~(mask << out_pos)
        csr_word_array[out_idx] |= (fld_word_array[in_idx] & mask) << out_pos

        # determine if we need to read part of the next word
        if (write_upper):
            # need to read the remaining bits in this input word
            if (constants.WORD_SIZE_BITS < rem_size):
                out_size_hi = constants.WORD_SIZE_BITS - out_size
            else:
                out_size_hi = rem_size - out_size
            if not (out_size_hi < constants.WORD_SIZE_BITS): # can't be constants.WORD_SIZE_BITS, would be read above
                sys.exit(1)

            # construct the mask
            mask = (0x1 << out_size_hi) - 1

            # or in the value
            if not (out_idx > 0):
                sys.exit(1)
            csr_word_array[out_idx-1] &= ~mask
            csr_word_array[out_idx-1] |= (fld_word_array[in_idx] >> out_size) & mask
        else:
            out_size_hi = 0

        logger.debug(("rem_size: {0}, in_size: {1}, in_size_hi: {2} = {3}").format(
               rem_size, out_size, out_size_hi, rem_size -  out_size + out_size_hi))

        # next output word
        in_idx -= 1
        rem_size -= out_size + out_size_hi

    return csr_word_array

def csr_get_valid_field_list(csr_data):
    field_list_obj = csr_data.get("fld_lst", None)
    field_list = dict()
    for f in field_list_obj:
        fld_name = f.get('fld_name', None)
        #if fld_name is not '__rsvd' or fld_name is not None:
        if fld_name is not None:
            field_list[fld_name] = f
    return field_list

def csr_show(csr_data, word_array, field_list=None):
    if len(word_array) != (csr_get_width_bytes(csr_data) >> 3):
        print("csr_width: {0} word_array length: {1}".format(
            csr_get_width_bytes(csr_data), len(word_array)))
        print("Invalid arguments! word array length should match csr width!")
        return

    if field_list is not None:
        field_list = list(set(field_list))

    print("csr raw: {0}".format(hex_word_dump(word_array)))
    fields_objs = csr_data.get("fld_lst", None)
    for f in fields_objs:
        fld_name = f.get('fld_name', None)
        if field_list is not None and fld_name not in field_list:
            continue
        fld_width = f.get('fld_width', None)
        fld_offset = f.get('fld_offset', None)
        field_word_array = csr_get_field(fld_offset, fld_width, word_array)
        if not field_word_array:
            print("Error! Failed to extract field:{0}".format(fld_name))
            return
        print("\t{0}: {1}".format(fld_name, hex_word_dump(field_word_array)))
        if field_list:
            field_list.remove(fld_name)
    if field_list:
        field_list_valid = csr_get_valid_field_list(csr_data).keys()
        print(("Skipped invalid fields:"
              " {0}\nvalid fields: {1}").format(field_list, field_list_valid))

# prints as array of hex integers
def hex_word_dump(word_array):
    hex_word_array = '['
    for w in word_array:
        hex_word_array += '0x{:016x}'.format(w)
    hex_word_array =  hex_word_array
    hex_word_array += ']'
    return hex_word_array

# Treat string digit as decimal and string prefixed with "0x" as hex
# and convert it as an integer
def str_to_int(s):
    if s.isdigit():
        try:
            return int(s, 10)
        except ValueError:
            return None
    try:
        return int(s, 0)
    except ValueError:
        return None

    return None

# Returns json pretty string
def json_obj_pretty(json_obj):
    return json.dumps(json_obj, indent=4)

# Returns all list of csrs from csr metadata
def get_csr_list():
    return csr_metadata().get_csr_list()

# Returns abosolute path for a file
def get_file_abs_path(loc):
    if not os.path.isabs(loc):
        loc = os.path.join(os.getcwd(), loc)
    assert os.path.exists(loc), "{}: directory does not exist!".format(loc)
    return loc

def csr_get_metadata(csr_name, csr_inst=None, csr_entry=None, ring_name=None,
                ring_inst=None, anode_name=None, anode_inst=None, anode_path=None):
    if not csr_name:
        print("csr name is empty! Provide valid csr name!")
        return

    csr_list = csr_metadata().get_csr_def(csr_name)
    if csr_list is None:
        print("csr: {} doesnot exist in database!.".format(csr_name))
        return

    rings = dict()
    logger.debug("Preparing ring list")
    for csr in csr_list:
        rname = csr.get("ring_name", None)
        if rings.get(rname, None) is None:
            rings[rname] = list()
        if csr.get("ring_inst", None) not in rings[rname]:
            rings[rname].append(csr.get("ring_inst", None))
        logger.debug("ring name:{} inst:{}".format(rname, csr.get("ring_inst", None)))

    if len(rings) == 0:
        print("Inconsistant csr metadata parsing!")
        return

    print("rings: {}".format(rings))
    if len(rings) > 0:
        print("csr_name: {} ring_name: {}".format(csr_name, ring_name))
        if len(rings) > 1 and ring_name is None:
            print("csr objs:\n{}\n".format(json_obj_pretty(csr_list)))
            print(("csr: {} exists in multiple rings."
                   " Give appropriate ring option! valid rings: {}").format(csr_name, rings))
            return
        if ring_name not in rings:
            print("csr objs:\n{}\n".format(json_obj_pretty(csr_list)))
            print(("Invalid ring:{} for csr: {}."
                   " Give appropriate ring option! valid rings: {}").format(ring_name,
                                                                            csr_name, rings))
            return

        csr_list = csr_metadata().get_csr_def(csr_name = csr_name, rn_class=ring_name)
        ring_inst_list = rings.get(ring_name)
        print("ring: {} instace list: {}".format(ring_name, ring_inst_list))
        if len(ring_inst_list) > 0:
            if len(ring_inst_list) > 1 and ring_inst is None:
                print("csr objs:\n{}\n".format(json_obj_pretty(csr_list)))
                print(("csr: {} exists in multiple instances of ring: {}."
                       "\nGive appropriate ring option! valid rings instances:"
                       "{}").format(csr_name, ring_name, ring_inst_list))
                return
            print("ring name: {}  inst: {}".format(ring_name, ring_inst))
            if ring_inst not in ring_inst_list:
                print("csr objs:\n{}\n".format(json_obj_pretty(csr_list)))
                print(("Invalid ring instance for csr: {} ring: {}."
                      "\nGive appropriate ring details! valid rings instances:"
                       "{}").format(csr_name, ring_name, ring_inst_list))
                return

    anodes = dict()
    csr_list = csr_metadata().get_csr_def(csr_name = csr_name,
                                          rn_class=ring_name, rn_inst=ring_inst)
    logger.debug("Preparing anode list")
    for csr in csr_list:
        if ring_name == csr.get("ring_name", None):
            an_name = csr.get("an", None)
            logger.debug(an_name)
            anodes[an_name] = csr.get("an_inst_cnt", None)
    print("anodes: {}".format(anodes))
    if anodes and len(anodes) > 1:
        if anode_name is None:
            print("csr objs:\n{}\n".format(json_obj_pretty(csr_list)))
            print(("csr: {} exists in multiple anodes."
                  "\nGive appropriate anode option! valid anodes: {}").format(csr_name, anodes))
            return
        if anode_name not in anodes:
            print("csr objs:\n{}\n".format(json_obj_pretty(csr_list)))
            print(("Invalid anode:{} for csr: {}."
                   "\nGive appropriate anode option! valid anodes: {}").format(anode_name,
                                                                csr_name, anodes))
            return

    csr_list = csr_metadata().get_csr_def(csr_name = csr_name,
                                rn_class=ring_name, rn_inst=ring_inst, an=anode_name)

    anode_inst_count = 0;
    if anode_name is not None:
        anode_inst_count = anodes.get(anode_name, 0)
        print("anode: {} inst count: {}".format(anode_name, anode_inst_count))
        if not anode_inst_count > 0:
            print("Inconsistant csr metadata parsing!")
            return
    if anode_inst_count > 0:
        if anode_inst_count > 1 and anode_inst is None:
            print("csr objs:\n{}\n".format(json_obj_pretty(csr_list)))
            print(("csr: {} exists in multiple instances of anode: {}."
                   " Give appropriate anode option!"
                   " valid anode instances: {}").format(csr_name,
                            anode_name, range(0,anode_inst_count)))
            return

        if (anode_inst is not None) and (anode_inst < 0 or anode_inst >= anode_inst_count):
            print("csr objs:\n{}\n".format(json_obj_pretty(csr_list)))
            print(("Invalid anode instance for csr: {} anode: {}."
                "\nGive appropriate anode details!"
                " Valid anode instances: {}").format(csr_name,
                anode_name, range(0,anode_inst_count)))
            return

    if len(csr_list) != 1:
        print("csr objs:\n{}\n".format(json.dumps(csr_list, indent=4)))
        print("more than one csr instance! Inconsistant csr metadata parsing!")
        return

    csr = csr_list[0]
    csr_count = csr.get("csr_count", None)
    if csr_count > 1:
        if csr_inst is None:
            print("csr objs:\n{}\n".format(json.dumps(csr, indent=4)))
            print(("There are {} instances of csr:{}."
                   "\nProvide csr instance number!".format(csr_count,
                                                           csr_name)))
            return
        if csr_inst < 0 or csr_inst >= csr_count:
            print("csr objs:\n{}\n".format(json.dumps(csr, indent=4)))
            print(("Invalid instances of csr:{}."
                   "\nProvide csr instance number in the"
                   " range [0 - {}]!").format(csr_name, csr_count - 1))
            return
    if csr_count == 1 and csr_inst is not None:
        print("**** Ignoring option csr instance number: {}!!! ****".format(csr_inst))


    csr_n_entries = csr.get("csr_n_entries", None)
    if csr_n_entries > 1:
        if csr_entry is None:
            print("csr objs:\n{}\n".format(json.dumps(csr_list, indent=4)))
            print(("There are {} entries in table csr:{}."
                   "\nProvide csr entry index number!").format(csr_n_entries, csr_name))
            return
        print("csr entry index: {} csr_n_entries: {}".format(csr_entry, csr_n_entries))
        if csr_entry < 0 or csr_entry >= csr_n_entries:
            print("csr objs:\n{}\n".format(json.dumps(csr, indent=4)))
            print(("Invalid entry index of csr:{}."
                   "\nProvide csr entry index in the"
                   " range of [0 - {}]!".format(csr_name,
                                                csr_n_entries - 1)))
            return
    if csr_n_entries == 1 and csr_entry is not None:
        print("**** Ignoring option csr entry index: {}!!! ****".format(csr_entry))

    logger.debug("Found CSR: \n{}\n".format(json.dumps(csr, indent=4)))
    return csr

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

# Create single instance of csr metadata
@singleton
class csr_metadata:
    def __init__(self):
        status = self.load_metadata_from_dochub()
        if not status:
             print('Failed to load csr metadata!')
             sys.exit(1)

    def _load_metadata_file(self, metadata_file):
        if not os.path.exists(metadata_file):
            print "Failed to find matadata file: {}".format(metadata_file)
            return False
        print("Loading csr metadata: {0}".format(metadata_file))
        self.metadata = json.load(open(metadata_file))
        return True

    def download_metadata_from_dochub(self):
        metadata_file = os.path.join(constants.TMP_DIR,
                    constants.CSR_CFG_DIR, constants.CSR_METADATA_FILE)
        if os.path.exists(metadata_file): os.remove(metadata_file)
        try:
            csr_metadata_dochub()
        except Exception as e:
            logging.error(traceback.format_exc())
            print('Failed to get csr metadata from dochub!'
                  'Make sure that "dochub.fungible.local" accessable.')
            return None
        if not os.path.exists(metadata_file):
            print "Failed to find matadata file: {} after download!".format(metadata_file)
            return None
        return metadata_file

    def load_metadata_from_dochub(self):
        status = self.download_metadata_from_dochub()
        if not status:
             print('Failed to download csr metadata!')
             return False
        metadata_file = os.path.join(constants.TMP_DIR,
                    constants.CSR_CFG_DIR, constants.CSR_METADATA_FILE)
        if not os.path.exists(metadata_file):
            print "Failed to find matadata file: {} after download!".format(metadata_file)
            return None
        status = self._load_metadata_file(metadata_file)
        if not status:
            return False
        return True

    def load_metadata_from_sdk(self, sdk_root):
        metadata_file = os.path.join(sdk_root, constants.CSR_CFG_DIR,
                constants.CSR_METADATA_FILE)
        if not os.path.exists(metadata_file):
            print "Failed to find matadata file: {}".format(metadata_file)
            return None
        status = self._load_metadata_file(metadata_file)
        if not status:
            print "Failed to load matadata file: {}".format(metadata_file)
            return False
        return True

    def get_metadata(self):
        return self.metadata

    def csr_equal(self, x, rn_class, rn_inst, an_path, an):
        if rn_class:
            if x["ring_name"] != rn_class:
                return False
        if rn_inst:
            if x["ring_inst"] != rn_inst:
                return False
        if an:
            if x["an"] != an:
                return False
        if an_path:
            if x["an_path"] != an_path:
                return False

        return True

    def get_csr_def(self, csr_name, rn_class=None, rn_inst=None,
                    an_path=None, an=None):
        csr_defs_lst = self.metadata.get(csr_name, [])
        if not csr_defs_lst:
            return None
        else:
            csr_defs_lst = [x for x in csr_defs_lst        \
                            if self.csr_equal(x, rn_class, \
                            rn_inst, an_path, an)]

        return csr_defs_lst

    def get_csr_list(self):
        return list(self.metadata.keys())

    def csr_inst_verify(self, csr_name):
        csr_list = self.get_csr_def(csr_name=csr_name)

