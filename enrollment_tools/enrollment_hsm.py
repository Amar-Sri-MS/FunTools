#!/usr/bin/env python3
# HSM Key management for SBP
# Copyright (c) 2018-2019 Fungible,inc. All Rights reserved.
#
# Implements the following commands:
#
# list: list all RSA keys in the HSM for the token
# create: create a RSA key
# remove: remove the key from the HSM
# modulus: print the modulus of the key
# import: import a key into the hsm
# x509: generate a self signed X509 certificate

import os, struct, binascii, argparse, sys, datetime
import getpass

import pkcs11
import pkcs11.util.rsa
from asn1crypto import core, pem, keys, x509

# FIXME: this should be a shared constants file
RSA_KEY_SIZE_IN_BITS = 2048


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


def write(filename, content, overwrite=True, tobyte=False, verbose=False):
    if not filename:
        return
    if verbose:
        print("Writing %s" % filename)
    # Overwrite
    if not overwrite and os.path.exists(filename):
        raise Exception("File '%s' already exists" % filename)
    # Open
    try:
        if filename == '-' or filename is None:
            f = sys.stdout.buffer
        else:
            f = open(filename, "wb")
    except:
        raise Exception("Cannot open file '%s' for write" % filename)
    # Write
    if tobyte:
        for pos in range(0, len(content)):
            f.write("%s\n" % binascii.b2a_hex(content[pos]).decode('ascii'))
    else:
        f.write(content)



def get_from_user(prompt):
    ''' a slighty fancier to get the user to enter data '''
    while True:
        res = eval(input(prompt))
        ok = eval(input("You entered '{0}'\nIs this correct? (Y/n) ".format(res)))
        if ok == '' or ok == 'Y' or ok == 'y':
            break

    return res


# libraries in order of preference -- second argument: prompt for password
LIBSOFTHSM2_PATHS = [
    ("/usr/safenet/lunaclient/lib/libCryptoki2_64.so"), # Safenet ubuntu 14
    ("/usr/lib/softhsm/libsofthsm2.so"), # Ubuntu-17, 18
    ("/usr/lib/x86_64-linux-gnu/softhsm/libsofthsm2.so"), # Ubuntu-16
    ("/usr/local/lib/softhsm/libsofthsm2.so"), # macOS brew
    ("/project/tools/softhsm-2.3.0/lib/softhsm/libsofthsm2.so"), # shared vnc machines for verification team
]

def get_token_label():
    return get_from_user("Token Label = ")

def get_pkcs11_lib():

    lib = None

    for entry in LIBSOFTHSM2_PATHS:
        if os.path.exists(entry):
            try:
                lib = pkcs11.lib(entry)
            except:
                pass

            if lib is not None:
                break

    if lib is None:
        raise RuntimeError("Could not find PKCS#11 library")

    return lib

def get_token(token_label):
    lib = get_pkcs11_lib()

    if token_label == '' or token_label is None:
        token_label = get_token_label()

    print("Using token %s" % token_label)

    password = getpass.getpass()

    # look into the slots with token
    # the old lib.get_token does not work well with Safenet PKCS#11
    for slot in lib.get_slots(True):
        token = slot.get_token()
        if token.label == token_label:
            return token, password
    print("No such token")
    sys.exit(1)

def get_modulus(pub):
    return pub[pkcs11.Attribute.MODULUS]

def get_exponent(pub):
    return pub[pkcs11.Attribute.PUBLIC_EXPONENT]

def generate_rsa_key_pair(rw_session, label):
    ''' Create and returns a new RSA key pair in the store '''
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

def create_rsa(token_name, label):

    token, password = get_token(token_name)

    public_modulus = None
    # Open a session on our token
    with token.open(user_pin=password, rw=False) as session:
        try:
            public = get_public_rsa_with_label(session, label)
            public_modulus = get_modulus(public)

        except Exception as err:
            print(err)

    if public_modulus is None:
        with token.open(user_pin=password, rw=True) as session:
            print("Generating key " + label)
            public, _ = generate_rsa_key_pair(session, label)
            public_modulus = get_modulus(public)
            print("Key created: modulus:")
    else:
        print("Key with the label '%s' already exists:" % label)

    print("%s" % binascii.b2a_hex(public_modulus).decode('ascii'))


def list_all_keys(token_name):
    ''' list all the keys in the session '''
    token, password = get_token(token_name)

    # Open a session on our token
    with token.open(user_pin=password, rw=False) as session:
        all_publics = list(session.get_objects(
            {pkcs11.Attribute.CLASS: pkcs11.ObjectClass.PUBLIC_KEY,
             pkcs11.Attribute.KEY_TYPE: pkcs11.KeyType.RSA}))

        for obj in all_publics:
            print(obj)
            modulus = get_modulus(obj)
            print("Modulus:")
            print(binascii.b2a_hex(modulus).decode('ascii'))
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


def remove_key(token_name, label):
    ''' delete that key from the HSM '''
    token, password = get_token(token_name)

    # Open a session on our token
    with token.open(user_pin=password, rw=True) as session:
        remove_key_aux(session,label)

def import_key(token_name, infile, label):
    ''' import a key from a PEM file into the HSM '''

    # try to read an RSA key from the infile
    try:
        data = read(infile)
        if pem.detect(data):
            _,_, data = pem.unarmor(data)
        priv_key = pkcs11.util.rsa.decode_rsa_private_key(data)
    except Exception as ex:
        print("Unable to read key file " + infile + " Error = " + str(ex))
        return

    token, password = get_token(token_name)

     # Open a session on our token
    with token.open(user_pin=password, rw=True) as session:
        try:
            existing = get_public_rsa_with_label(session, label)
            if existing is not None:
                print("Found key with label '" + label + "'")

            # compare
            if get_modulus(existing) == get_modulus(priv_key) and get_exponent(existing) == get_exponent(priv_key):
                print("Matching key '" + label + "' already imported")
                return
            else:
                print("Replacing existing key '" + label + "'")
                existing.destroy()
                remove_key_aux(session, label)
        except Exception as ex:
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


def export_pub_key(token_name, outfile, label, c_source):
    ''' modulus of key '''
    token, password = get_token(token_name)

    # Open a session on our token
    with token.open(user_pin=password, rw=False) as session:
        try:
            public = get_public_rsa_with_label(session, label)
            modulus = get_modulus(public)

        except Exception as err:
            print(err)
            return

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

    write(outfile, modulus)


def prompt_for_values(prefix, values):

    responses = {}
    once_again = True
    while once_again:
        for value in values:
            res = eval(input(prefix + " " + value["prompt"] + " (" + value["default"] + "): "))
            if res == "":
                res = value["default"]
            responses[value["key"]] = res

        print("\nYou entered the following for " + prefix + ":\n")
        for value in values:
            print("%s: %s" % (prefix + " " + value["prompt"], responses[value["key"]]))
        ok = eval(input("\nIs this correct? (Y/n)"))
        if ok in ['','Y','y']:
            break

    return responses


def get_x509_name(prefix):

    COUNTRY = { "key": "country_name", "prompt":"Country", "default":"US"}
    STATE = { "key": "state_or_province_name", "prompt" : "State Or Province", "default": ""}
    LOCALITY = { "key": "locality_name", "prompt":"Locality", "default":""}
    ORGANIZATION = { "key": "organization_name", "prompt" : "Organization", "default": "Fungible,Inc."}
    CN = { "key": "common_name", "prompt" : "Common Name", "default": ""}
    NAME_PARTS = [COUNTRY, STATE, LOCALITY, ORGANIZATION, CN]

    responses = prompt_for_values(prefix, NAME_PARTS)
    filled_responses = {k : v for k,v in list(responses.items()) if v}
    return x509.Name.build(filled_responses)


def get_x509_validity():
    VALIDITY = [{ "key": "days", "prompt" : "Days valid", "default": "90" }]

    responses = prompt_for_values("", VALIDITY)
    not_before = x509.UTCTime()
    not_before.set(datetime.datetime.utcnow())
    not_after = x509.UTCTime()
    not_after.set(datetime.datetime.utcnow()+datetime.timedelta(days=int(responses["days"],0)))

    validity = x509.Validity()
    validity['not_before'] = not_before
    validity['not_after'] = not_after
    return validity

def gen_rsa_pub_key_info(modulus, exponent=0x10001):
    rsa = keys.RSAPublicKey()
    rsa['modulus'] = int.from_bytes(modulus, byteorder='big')
    rsa['public_exponent'] = exponent
    return keys.PublicKeyInfo.wrap(rsa, "rsa")

def gen_basic_constraints(critical, ca, path_len=None):

    basic_constraints = x509.BasicConstraints()
    basic_constraints['ca'] = ca
    if path_len:
        basic_constraints['path_len_contraint'] = path_len
    bc_extension = x509.Extension()
    bc_extension['extn_id'] = 'basic_constraints'
    bc_extension['critical'] = critical
    bc_extension['extn_value'] = basic_constraints
    return bc_extension

def gen_key_usage(critical, key_usages):
    key_usage = x509.KeyUsage()
    key_usage.set(key_usages)
    ku_extension = x509.Extension()
    ku_extension['extn_id'] = 'key_usage'
    ku_extension['critical'] = critical
    ku_extension['extn_value'] = key_usage
    return ku_extension

def gen_key_identifier(pub_key_info):
    key_id = core.OctetString()
    key_id.set(pub_key_info.sha1)
    ki_extension = x509.Extension()
    ki_extension['extn_id'] = 'key_identifier'
    ki_extension['critical'] = False
    ki_extension['extn_value'] = key_id
    return ki_extension


def create_x509(token_name, out_path, out_format, key_label):

    cert = x509.Certificate()
    tbs = x509.TbsCertificate()

    tbs['version'] = 2
    tbs['serial_number'] = 1

    # build signature
    signature = x509.SignedDigestAlgorithm()
    signature['algorithm'] = 'sha512_rsa'
    tbs['signature'] = signature

    # cert signature algorithm
    cert['signature_algorithm'] = signature

    tbs['issuer'] = get_x509_name("")
    tbs['subject'] = tbs['issuer']

    # build the validity
    tbs['validity']= get_x509_validity()

    # extensions: basic constraints, key usage (key_cert_sign, crl_sign), subject key id
    extensions = x509.Extensions()
    extensions.append(gen_basic_constraints(True, True))
    extensions.append(gen_key_usage(True, set(['key_cert_sign', 'crl_sign'])))
    tbs['extensions'] = extensions

    # rest requires the HSM
    token, password = get_token(token_name)

    # Open a session on our token
    with token.open(user_pin=password, rw=False) as session:
        the_key = get_private_rsa_with_label(session, key_label)
        subject_pub_key_info = gen_rsa_pub_key_info(get_modulus(the_key))
        tbs['subject_public_key_info'] = subject_pub_key_info
        tbs['extensions'].append(gen_key_identifier(subject_pub_key_info))
        cert['tbs_certificate'] = tbs
        raw_signature = the_key.sign( tbs.dump(), mechanism=pkcs11.Mechanism.SHA512_RSA_PKCS)

    bit_str = core.OctetBitString()
    bit_str.set(raw_signature)
    cert['signature_value'] = bit_str

    der_bytes = cert.dump()

    if out_format == 'DER':
        out_bytes = der_bytes
    else:
        out_bytes = pem.armor('CERTIFICATE', der_bytes)

    with open(out_path, 'wb') as f:
        num_bytes = f.write(out_bytes)

    print("Certificate written in %s format: %s (%d bytes)" %
          (out_format, out_path, num_bytes))

def parse_and_execute():
    parser = argparse.ArgumentParser()

    parser.add_argument("command",
                        help="command to execute: list, create, import, remove, modulus, x509")

    parser.add_argument("-k", "--key", dest="key_label",
                        help="key label (create, remove, modulus)")

    parser.add_argument("-f", "--format", dest="out_format",
                        choices=["PEM,DER"], default="PEM",
                        help="X509 output format: PEM (Default), DER")

    parser.add_argument("-i", "--input",  dest="in_path",
                        help="input file name", metavar="FILE")

    parser.add_argument("-o", "--output", dest="out_path",
                        help="location to output to", metavar="FILE")

    parser.add_argument("-s", "--source", dest="c_source",
                        action='store_true',
                        help="ouput key in C hexadecimal format")

    parser.add_argument("-t", "--token", dest="token",
                        help="HSM token name")



    options = parser.parse_args()

    if options.command == 'list':

        list_all_keys(options.token)
        sys.exit(0)

    elif options.key_label is None:

        print("Key label required for the command %s" % options.command)
        sys.exit(1)


    if options.command == 'remove':
        remove_key(options.token, options.key_label)
    elif options.command == 'modulus':
        export_pub_key(options.token, options.out_path,
                       options.key_label, options.c_source)
    elif options.command == 'create':
        create_rsa(options.token, options.key_label)
    elif options.command == 'import':
        import_key(options.token, options.in_path, options.key_label)
    elif options.command == 'x509':
        create_x509(options.token, options.out_path, options.out_format,
                    options.key_label)



if __name__ == "__main__":
    parse_and_execute()
