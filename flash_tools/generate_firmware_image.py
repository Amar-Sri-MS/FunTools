#!/usr/bin/env python3
# HSM Key management for SBP
# Copyright (c) 2018 Fungible,inc. All Rights reserved.
#
# Implements the following commands:
#
# list: list all RSA keys in the HSM for the token
# image: generate an image signed by a key or a certificate
# modulus: export the modulus of a RSA key, in binary or in C source code format
# certificate: generate a certificate
# sign: append a signature to the input
# remove: remove the key from the HSM
# hash: generate the SHA256 hash of a key


import os, struct, binascii, argparse, sys
import traceback, getpass, datetime, configparser
import fcntl

import pkcs11
import pkcs11.util.rsa
from asn1crypto import pem

# FIXME: this should be a shared constants file
RSA_KEY_SIZE_IN_BITS = 2048
SIGNING_INFO_SIZE = 2048
MAX_SIGNATURE_SIZE = 512
HEADER_RESERVED_SIZE = SIGNING_INFO_SIZE - (4 + MAX_SIGNATURE_SIZE)
SIGNED_ATTRIBUTES_SIZE = 64
SERIAL_INFO_NUMBER_SIZE = 24
CERT_PUB_KEY_POS = 64

MAGIC_NUMBER_CERTIFICATE = 0xB1005EA5
MAGIC_NUMBER_ENROLL_CERT = 0xB1005C1E


def get_from_user(prompt):
    ''' a slighty fancier to get the user to enter data '''
    while True:
        res = input(prompt)
        ok = input("You entered '{0}'\nIs this correct? (Y/n) ".format(res))
        if ok == '' or ok == 'Y' or ok == 'y':
            break

    return res


##############################################################################
# File access -- utils.py ported to Python 3
##############################################################################

def read(filename, nbytes=None, verbose=False):
    if filename is None:
        return ""
    if verbose:
        print("Reading %s" % filename)
    try:
        if filename == '-':
            txt = sys.stdin.buffer.read()
        else:
            txt = open(filename, "rb").read()
    except:
        raise Exception("Cannot open file '%s' for read" % filename)
    if nbytes and len(txt) != nbytes:
        raise Exception("File '%s' has invalid length. Expected %d, got %d"
                        % (filename, nbytes, len(txt)))
    return txt

def write(filename, content, overwrite=True, tohex=False, tobyte=False, verbose=False):
    if not filename:
        return
    if verbose:
        print("Writing %s" % filename)
    # Overwrite
    if not overwrite and os.path.exists(filename):
        raise Exception("File '%s' already exists" % filename)
    # Open
    try:
        if filename == '-':
            f = sys.stdout.buffer
        else:
            f = open(filename, "wb")
    except:
        raise Exception("Cannot open file '%s' for write" % filename)
    # Write
    if tohex:
        assert len(content)%4 == 0
        for pos in range(0, len(content), 4):
            f.write("%08X\n" % struct.unpack("<I", content[pos:pos+4]))
    elif tobyte:
        for pos in range(0, len(content)):
            f.write("%s\n" % binascii.hexlify(content[pos]))
    else:
        f.write(content)


class Lock:

    def __init__(self, filename):
        self.filename = filename
        # This will create it if it does not exist already
        self.handle = open(filename, 'w')

    # Bitwise OR fcntl.LOCK_NB if you need a non-blocking lock
    def acquire(self):
        fcntl.flock(self.handle, fcntl.LOCK_EX)

    def release(self):
        fcntl.flock(self.handle, fcntl.LOCK_UN)

    def __del__(self):
        self.handle.close()

# libraries in order of preference -- second argument: prompt for password
LIBSOFTHSM2_PATHS = [
    ("/usr/safenet/lunaclient/lib/libCryptoki2_64.so", True), # Safenet ubuntu 14
    ("/usr/lib/softhsm/libsofthsm2.so", False), # Ubuntu-17, 18
    ("/usr/lib/x86_64-linux-gnu/softhsm/libsofthsm2.so", False), # Ubuntu-16
    ("/usr/local/lib/softhsm/libsofthsm2.so", False), # macOS brew
    ("/project/tools/softhsm-2.3.0/lib/softhsm/libsofthsm2.so", False), # shared vnc machines for verification team
]

def get_token_label():
    return get_from_user("Token Label = ")

def get_pkcs11_lib():

    lib = None
    prompt = False

    for entry in LIBSOFTHSM2_PATHS:
        if os.path.exists(entry[0]):
            try:
                lib = pkcs11.lib(entry[0])
            except:
                pass

            if lib is not None:
                prompt = entry[1]
                break

    if lib is None:
        raise RuntimeError("Could not find PKCS#11 library")

    return lib, prompt


def get_token():
    lib, prompt = get_pkcs11_lib()

    if prompt:
        token_label = get_token_label()
        password = getpass.getpass()
    else:
        token_label = 'fungible_token'
        password = 'fungible'

    # look into the slots with token
    # the old lib.get_token does not work well with Safenet PKCS#11
    for slot in lib.get_slots(True):
        token = slot.get_token()
        if token.label == token_label:
            return token, password


def log_op(operation):
    # log the operation -- python share files
    log_name = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            ".fungible_hsm.log")
    with open(log_name, "a") as log_file:
        log_file.write("%s: date = %s user = %s\n" % (operation,
                                                      str(datetime.datetime.now()),
                                                      getpass.getuser()))
        traceback.print_stack(file=log_file)


def generate_rsa_key_pair(rw_session, label):
    ''' Create and returns a new RSA key pair in the store '''
    log_op("Create key " + label)
    return rw_session.generate_keypair(key_type=pkcs11.KeyType.RSA,
                                       id=binascii.hexlify(label.encode()),
                                       key_length=RSA_KEY_SIZE_IN_BITS,
                                       label=label,
                                       store=True)

def get_private_rsa_with_label(ro_session, label):
    return ro_session.get_key(object_class=pkcs11.constants.ObjectClass.PRIVATE_KEY,
                              label=label)


def get_public_rsa_with_label(ro_session, label):
    ''' Returns public key '''
    return ro_session.get_key(object_class=pkcs11.constants.ObjectClass.PUBLIC_KEY,
                              label=label)

def get_private_rsa_with_modulus(ro_session, modulus):
    ''' retrieve the private key with the modulus specified '''
    private = None
    try:
        privates = ro_session.get_objects({pkcs11.Attribute.CLASS:pkcs11.ObjectClass.PRIVATE_KEY,
                                           pkcs11.Attribute.KEY_TYPE:pkcs11.KeyType.RSA,
                                           pkcs11.Attribute.MODULUS:modulus})
        private = next(privates)
    except Exception as err:
        print(err)

    return private

def get_create_public_rsa_modulus(label, hash=None):

    token, password = get_token()

    public_modulus = None
    # Open a session on our token
    with token.open(user_pin=password, rw=False) as session:
        try:
            public = get_public_rsa_with_label(session, label)
            public_modulus = get_modulus(public)
            if hash is not None:
                return session.digest(public_modulus, mechanism=hash)

        except Exception as err:
            print(err)

    if public_modulus is None:
        with token.open(user_pin=password, rw=True) as session:
            print("Generating key " + label)
            public, _ = generate_rsa_key_pair(session, label)
            public_modulus = get_modulus(public)
            if hash is not None:
                return session.digest(public_modulus, mechanism=hash)

    return public_modulus


def sign_with_rsa_key(label, data):

    token, password = get_token()

    # Open a session on our token
    with token.open(user_pin=password, rw=False) as session:
        try:
            private = get_private_rsa_with_label(session, label)
        except Exception as err:
            print(err)
            print("Keys can be created  with the 'public' command")
            raise

        return private.sign(data, mechanism=pkcs11.Mechanism.SHA512_RSA_PKCS)

def get_cert_modulus(cert):
    cert_key_modulus_len = struct.unpack('<I', cert[CERT_PUB_KEY_POS:CERT_PUB_KEY_POS+4])
    start = CERT_PUB_KEY_POS+4
    end = start + cert_key_modulus_len[0]
    return cert[start:end]

def sign_with_cert(cert, data):
    token, password = get_token()
    modulus = get_cert_modulus(cert)
    # Open a session on our token
    with token.open(user_pin=password, rw=False) as session:
        private = get_private_rsa_with_modulus(session, modulus)
        if private is not None:
            # when we sign with a cert, the certificate itself is included
            # in the signature, to prevent mix and match if several certificates
            # use the same key.
            return private.sign(cert+data, mechanism=pkcs11.Mechanism.SHA512_RSA_PKCS)

    return b''

def get_modulus(pub):
    return pub[pkcs11.Attribute.MODULUS]

def get_exponent(pub):
    return pub[pkcs11.Attribute.PUBLIC_EXPONENT]

def append_signature_to_binary(binary, signature):
    binary += struct.pack('<I', len(signature))
    binary += signature
    # pad to MAX_SIGNATURE_SIZE with 0
    binary += b'\x00' * (MAX_SIGNATURE_SIZE - len(signature))
    return binary

def append_modulus_to_binary(binary, modulus):
    # same structure as signature and MAX_SIGNATURE_SIZE == MAX_MODULUS_SIZE
    return append_signature_to_binary(binary, modulus)

def list_all_keys():
    ''' list all the keys in the session '''
    token, password = get_token()

    # Open a session on our token
    with token.open(user_pin=password, rw=False) as session:
        all_publics = list(session.get_objects(
            {pkcs11.Attribute.CLASS: pkcs11.ObjectClass.PUBLIC_KEY,
             pkcs11.Attribute.KEY_TYPE: pkcs11.KeyType.RSA}))

        for obj in all_publics:
            print(obj)
            private = get_private_rsa_with_modulus(session, get_modulus(obj))
            if private:
                print("Corresponding private key:" + str(private))


def remove_key_aux(session, label):
    ''' delete key from the HSM using session'''
    try:
        private = get_private_rsa_with_label(session, label)
        if private:
            private.destroy()
    except:
        pass

    try:
        public = get_public_rsa_with_label(session, label)
        if public:
            public.destroy()
    except:
        pass


def remove_key(label):
    ''' delete that key from the HSM '''
    token, password = get_token()

    # Open a session on our token
    with token.open(user_pin=password, rw=True) as session:
        remove_key_aux(session,label)


def import_key(label, key_file):
    ''' import the key into the HSM if HSM allows it '''
    try:
        data = read(key_file)
        if pem.detect(data):
            _, _, data = pem.unarmor(data)
        priv_key = pkcs11.util.rsa.decode_rsa_private_key(data)
    except Exception as ex:
        print("Unable to read key file " + key_file + " Error = " + ex)
        return

    # Open a session on our token
    token, password = get_token()

    with token.open(user_pin=password, rw=True) as session:
        try:
            existing = get_public_rsa_with_label(session, label)
            # compare
            if get_modulus(existing) == get_modulus(priv_key) and get_exponent(existing) == get_exponent(priv_key):
                print("Key already imported")
                return
            else:
                print("Replacing existing key")
                existing.destroy()
                remove_key_aux(session, label)
        except:
            pass

        # add the key pairs
        priv_key[pkcs11.Attribute.LABEL] = label
        priv_key[pkcs11.Attribute.ID] = binascii.hexlify(label.encode())
        priv_key[pkcs11.Attribute.TOKEN] = True
        session.create_object(priv_key)

        #derive the public key
        pub_key = {}
        pub_key[pkcs11.Attribute.KEY_TYPE] = priv_key[pkcs11.Attribute.KEY_TYPE]
        pub_key[pkcs11.Attribute.PUBLIC_EXPONENT] = priv_key[pkcs11.Attribute.PUBLIC_EXPONENT]
        pub_key[pkcs11.Attribute.MODULUS] = priv_key[pkcs11.Attribute.MODULUS]
        pub_key[pkcs11.Attribute.CLASS] = pkcs11.ObjectClass.PUBLIC_KEY
        pub_key[pkcs11.Attribute.ENCRYPT] = True
        pub_key[pkcs11.Attribute.VERIFY] = True
        pub_key[pkcs11.Attribute.WRAP] = True
        pub_key[pkcs11.Attribute.LABEL] = label
        pub_key[pkcs11.Attribute.ID] = binascii.hexlify(label.encode())
        pub_key[pkcs11.Attribute.TOKEN] = True
        session.create_object(pub_key)



def export_pub_key(outfile, label, c_source):
    ''' modulus of key; create the key if it does not exist '''
    modulus = get_create_public_rsa_modulus(label)

    # export the modulus part of the public key
    if c_source:
        c_modulus = "%d,\n{\n" % len(modulus)

        for pos in range(0, len(modulus)):
            c_modulus += "0x%02x, " % modulus[pos]
            if pos % 8 == 7:
                c_modulus += "\n"
        if len(modulus) %8 != 0:
            c_modulus += "\n"
        c_modulus += "}"
        modulus  = c_modulus.encode()

    old_modulus = b''
    try:
        old_modulus = read(outfile)
    except:
        pass

    if old_modulus != modulus:
        write(outfile, modulus)
    else:
        print("No changes in modulus")

def export_pub_key_hash(outfile, label):
    ''' hash of modulus of key; create the key if it does not exist '''

    hash = get_create_public_rsa_modulus(label, hash=pkcs11.Mechanism.SHA256)

    # export the hash of the modulus of the public key

    old_hash = b''
    try:
        old_hash = read(outfile)
    except:
        pass

    if old_hash != hash:
        write(outfile, hash)
    else:
        print("No changes in hash")



def add_cert_and_signature_to_image(image, cert, signature):
    image += cert
    image += b'\x00' * (HEADER_RESERVED_SIZE - len(cert))
    return append_signature_to_binary(image, signature)


def image_gen(outfile, infile, ftype, version, sign_key,
	      certfile, customer_certfile):
    ''' generate signed firmware image '''
    binary = read(infile)
    to_be_signed = struct.pack('<2I', len(binary), version)
    to_be_signed += struct.pack('4s', ftype.encode())
    to_be_signed += b'\x00' * SIGNED_ATTRIBUTES_SIZE
    to_be_signed += binary

    signature = b''
    cert = b''
    # sign_key and cert_file are mutually exclusive
    if sign_key:
        signature = sign_with_rsa_key(sign_key, to_be_signed)
    elif certfile:
        cert = read(certfile)
        signature = sign_with_cert(cert, to_be_signed)
    elif not customer_certfile:
        print("A certificate ( customer or fungible) or a label is needed "+
              "to identify the key used to sign a firmware image")
        return

    customer_to_be_signed = add_cert_and_signature_to_image(b'', cert, signature)
    customer_to_be_signed += to_be_signed

    if customer_certfile:
        customer_cert = read(customer_certfile)
        customer_signature = sign_with_cert(customer_cert,
                                            customer_to_be_signed)
    else:
        customer_cert = b''
        customer_signature = b''

    image = add_cert_and_signature_to_image(b'', customer_cert,
                                            customer_signature)
    image += customer_to_be_signed

    write(outfile, image)


def sign_binary(binary, sign_key):
    ''' sign a binary and appends the signature to it '''
    signature = sign_with_rsa_key(sign_key, binary)
    return append_signature_to_binary(binary, signature)


def cert_gen(outfile, cert_key, cert_key_file, sign_key, serial_number,
             serial_number_mask, debugger_flags, tamper_flags):

    dflags = int(debugger_flags, 16)
    tflags = int(tamper_flags, 16)

    # MAGIC NUMBER, DEBUG FLAGS, 0, TAMPER FLAGS
    to_be_signed = struct.pack('<4I', MAGIC_NUMBER_CERTIFICATE, dflags, 0, tflags)

    # SERIAL NUMBER
    s_num = binascii.unhexlify(serial_number)
    if len(s_num) != SERIAL_INFO_NUMBER_SIZE:
        raise Exception("Serial Number length must be exactly " +
                        str(SERIAL_INFO_NUMBER_SIZE) + " bytes long")
    to_be_signed += s_num

    # SERIAL NUMBER MASK
    s_num_mask = binascii.unhexlify(serial_number_mask)
    if len(s_num_mask) != SERIAL_INFO_NUMBER_SIZE:
        raise Exception("Serial Number Mask length must be exactly " +
                        str(SERIAL_INFO_NUMBER_SIZE) + " bytes long")
    to_be_signed += s_num_mask

    if cert_key:
        # PUBLIC KEY: will be created if no such key
        modulus = get_create_public_rsa_modulus(cert_key)
    elif cert_key_file:
        # READ modulus from file
        modulus = read(cert_key_file)

    assert len(to_be_signed) == CERT_PUB_KEY_POS
    to_be_signed = append_modulus_to_binary(to_be_signed, modulus)

    # SIGNATURE
    cert = sign_binary(to_be_signed, sign_key)

    write(outfile, cert)

def raw_sign(out_path, in_path, sign_key):
    ''' raw sign: just sign the content and append the signature '''

    to_be_signed = read(in_path)
    signed = sign_binary(to_be_signed, sign_key)
    if out_path:
        write(out_path, signed)
    else:
        return signed


def parse_and_execute():
    parser = argparse.ArgumentParser()

    parser.add_argument("command", help="command to execute: list, remove, import, image, modulus, certificate, sign, hash")

    parser.add_argument("-c", "--certificate", dest="cert_path",
                        help="signing certificate (image)",
                        metavar="FILE")

    parser.add_argument("-d", "--debugger_flags", dest="debugger_flags",
                        default="00" * 4,
                        help="debugger_flags (hexadecimal, 4 bytes) (certificate)")

    parser.add_argument("-f", "--fwpath", dest="fw_path",
                        help="location of fw (image)",
                        metavar="FILE")

    parser.add_argument("-k", "--key", dest="sign_key",
                        help="signing key name (remove, import, image, certificate, modulus)")

    parser.add_argument("-m", "--serial_number_mask", dest="serial_number_mask",
                        default="FF" * SERIAL_INFO_NUMBER_SIZE,
                        help="serial number mask (hexadecimal, {0} bytes) (certificate)".format(SERIAL_INFO_NUMBER_SIZE))

    parser.add_argument("-n", "--serial_number", dest="serial_number",
                        help="serial number (hexadecimal, {0} bytes) (certificate)".format(SERIAL_INFO_NUMBER_SIZE))

    parser.add_argument("-o", "--output", dest="out_path",
                        help="location to output to", metavar="FILE")

    parser.add_argument("-p", "--public", dest="public_key",
                        help="public key name (certificate)")

    parser.add_argument("--public_key_file", dest="public_key_file",
                        help="public key file (certificate)", metavar="FILE")

    parser.add_argument("-r", "--rsa_key", dest="rsa_key",
                        help="RSA key to import in PEM or DER format (import)",
                        metavar="FILE")

    parser.add_argument("-s", "--source", dest="c_source",
                        action='store_true',
                        help="ouput key in C hexadecimal format")

    parser.add_argument("--serial_info_file", dest="serial_info_file",
                        help="file with serial number and mask", metavar="FILE")

    parser.add_argument("-t", "--fwtype", dest="fw_type",
                        help="fw type (4 chars) (image, certified_image)")

    parser.add_argument("-u", "--customer_certificate", dest="customer_cert_path",
                        help="customer certificate (image)", metavar="FILE")

    parser.add_argument("-v", "--fwver", dest="fw_ver",
                        help="fw version (image)")

    parser.add_argument("--tamper_flags", dest="tamper_flags",
                        default="00" * 4,
                        help="tamper_flags  (hexadecimal, 4 bytes) (certificate)")

    options = parser.parse_args()

    if options.command == 'list':

        list_all_keys()
        sys.exit(0)

    elif options.command == 'remove':

        if options.sign_key is None:
            print('Incorrect arg list (use -h for full info).')
            sys.exit(1)

        remove_key(options.sign_key)
        sys.exit(0)

    elif options.command == 'import':

        if options.sign_key is None:
            print('Incorrect arg list (use -h for full info).')
            sys.exit(1)

        if options.rsa_key is None:
            print('Incorrect arg list (use -h for full info).')
            sys.exit(1)

        import_key(options.sign_key, options.rsa_key)
        sys.exit(0)

    # all other commands require an out file
    if options.out_path is None:
        print('Incorrect arg list (use -h for full info).')
        sys.exit(1)

    if options.command == 'image':

        if options.fw_path is None:
            print('Incorrect arg list (use -h for full info).')
            sys.exit(1)

        if options.fw_ver is None:
            print('Incorrect arg list (use -h for full info).')
            sys.exit(1)

        if options.fw_type is None or len(options.fw_type) != 4:
            print('4 chars type required. Incorrect arg list (use -h for full info).')
            sys.exit(1)

        image_gen(options.out_path, options.fw_path, options.fw_type,
                  int(options.fw_ver, 0),
                  options.sign_key, options.cert_path,
                  options.customer_cert_path)

        sys.exit(0)


    # all other commands require a signing key
    if options.sign_key is None:
        print('Incorrect arg list (use -h for full info).')
        sys.exit(1)

    if options.command == 'modulus':

        export_pub_key(options.out_path, options.sign_key, options.c_source)

    elif options.command == 'hash':

        export_pub_key_hash(options.out_path, options.sign_key)

    elif options.command == 'certificate':

        # 2 possibilities to specify the serial number: cmd line or in file
        if options.serial_number is None and options.serial_info_file is None:
            print('Serial number required for certificate (Use -h for full info).')
            sys.exit(1)

        # 2 options to specify the public key: in HSM or in file
        if options.public_key is None and options.public_key_file is None:
            print('Public key required for certificate (use -h for full info).')
            sys.exit(1)

        # parse options.serial_info_file and do some checks
        # since this is what's used for real certificates
        if options.serial_number is None:
            with open(options.serial_info_file, 'r') as f:
                data = '[a_section]\n' + f.read()
            config = configparser.ConfigParser()
            config.read_string(data)

            options.serial_number=config.get('a_section','serial_number')
            options.serial_number_mask=config.get('a_section','serial_number_mask')
            sn = binascii.unhexlify(options.serial_number)
            snm = binascii.unhexlify(options.serial_number_mask)

            if len(sn) != SERIAL_INFO_NUMBER_SIZE:
               print( "Serial number is not completely specified in file  {0}".format(
                   options.serial_info_file))
               sys.exit(1)
            if len(snm) != SERIAL_INFO_NUMBER_SIZE:
               print( "Serial number mask is not completely specified in file  {0}".format(
                   options.serial_info_file))
               sys.exit(1)

        cert_gen(options.out_path, options.public_key, options.public_key_file,
                 options.sign_key, options.serial_number, options.serial_number_mask,
                 options.debugger_flags, options.tamper_flags)

    elif options.command == 'sign':

        if options.fw_path is None:
            print('Incorrect arg list (use -h for full info).')
            sys.exit(1)

        raw_sign(options.out_path, options.fw_path, options.sign_key)


if __name__ == "__main__":

    try:
        lock_file_name = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "hsm.lock")

        lock = Lock(lock_file_name)
        lock.acquire()
        # Do important stuff that needs to be synchronized
        parse_and_execute()

    finally:
        lock.release()
