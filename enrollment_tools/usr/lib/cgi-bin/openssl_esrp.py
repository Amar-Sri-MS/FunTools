#! /usr/bin/env python3

##############################################################################
#  openssl_esrp.py
#
#  signing routines using ESRP
#
#  Copyright (c) 2018-2020. Fungible, inc. All Rights Reserved.
#  Copyright (c) 2023. Microsoft Corporation. All Rights Reserved.
#
##############################################################################

''' Cryptographic operations using the OpenSSL ESRP engine '''


import os
import tempfile
import subprocess

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding, utils
from cryptography.hazmat.primitives.serialization import (load_pem_private_key,
                                                          load_pem_public_key,
                                                          load_der_public_key,
                                                          Encoding,
                                                          PublicFormat)

from common import DPU_REG_PATH
from config_esrp import check_token, read_json

####
# Constants
#


# maps the hashlib nams to the cryptolib hash algorithm
HASH_ALGO_NAMES = {
    "sha512" : hashes.SHA512,
    "sha256" : hashes.SHA256,
    "sha224" : hashes.SHA224,
    "sha384" : hashes.SHA384,
}

# path for well-known development keys
# map directly name to file: e.g. "fpk2" -> DEV_KEY_PATH/fpk2.pem
DEV_KEY_PATH=DPU_REG_PATH + 'keys'

# maps canonical key names to ESRP key
KEY_MAPPING=(
    {
        "fpk2"  : "CP-500109-Key",
        "fpk3"  : "CP-500110-Key",
        "fpk4"  : "CP-500111-Key",
        "fpk5"  : "CP-500112-Key",
        "cpk1"  : "CP-500113-Key",
        "cpk2"  : "CP-500114-Key",
        "hkey1" : "CP-500115-Key",
        "hkey2" : "CP-500116-Key",
        "hkey3" : "CP-500117-Key",
        "test"  : "CP-466286"  # works
    }
)

# Keys embedded in certs (sign_with_modulus)
KEY_IN_CERTS=("cpk1","cpk2")


ESRP_CONFIG_PATH=DPU_REG_PATH + 'esrpconfig.json'
ESRP_ENGINE_PATH='/opt/esrpengine/EsrpHelper'
CERT_CACHE_PATH=DPU_REG_PATH + 'certcache'

FULL_CONFIG_STR=f'certcache={CERT_CACHE_PATH};config={ESRP_CONFIG_PATH};helper={ESRP_ENGINE_PATH }'

#To use a special version of openssl
#OPENSSL_PATH='/usr/local/bin/openssl'
OPENSSL_PATH='openssl'

######################################################################
#
# cryptography helpers
#
######################################################################


def get_public_key(key: object) -> object:
    ''' return the public key from a public key or a private key '''
    try:
        key = key.public_key()
    except: #pylint: disable=bare-except
        pass
    return key

def key_n(key: object) -> int:
    ''' return modulus of key (private or public) '''
    return get_public_key(key).public_numbers().n


def int2bytes(n: int) -> bytes:
    ''' convert interger to big endian bytes '''
    return n.to_bytes((n.bit_length()+7) //8, byteorder='big')

def get_modulus_bytes(key: object) -> bytes:
    ''' return bytes of key modulus '''
    return int2bytes(key_n(key))


##################################################################
# Development keys: local PEM Files
#

def load_key_from_path(fname: str) -> object:
    ''' load key (private or public) from PEM file '''
    with open(fname, 'rb') as f_p:
        pem_data = f_p.read()
    banner_line = pem_data.splitlines()[0]

    if b'PRIVATE' in banner_line:
        return load_pem_private_key(pem_data,
                                    password=None,
                                    backend=default_backend())
    if b'PUBLIC' in banner_line:
        # this can load both PUBLIC KEY and RSA PUBLIC KEY
        return load_pem_public_key(pem_data,
                                   backend=default_backend())
    return None


def key_has_modulus(key: object, modulus: int) -> bool:
    ''' True if key has the same modulus (filter function) '''
    return modulus == key_n(key)


def search_paths_for_modulus( paths: list[str], modulus: int) -> object:
    ''' Search all paths for key with that modulus '''
    for curr_path in paths:
        key = load_key_from_path(curr_path)
        if key and key_has_modulus(key, modulus):
            return key
    return None

def get_key_with_label(key_label: str) -> object:
    ''' load key from PEM file '''
    key_path = os.path.join(DEV_KEY_PATH, key_label) + ".pem"
    key = load_key_from_path(key_path)
    return key


def get_key_with_modulus(modulus: bytes) -> object:
    ''' get key with modulus from PEM file collections '''
    # find key with that modulus
    # modulus to int
    target_n = int.from_bytes(modulus, byteorder='big')
    key = search_paths_for_modulus([e.path for e in os.scandir(DEV_KEY_PATH)
                                    if e.name.endswith('.pem')],
                                   target_n)
    if not key:
        raise ValueError(f"No key found for the modulus {hex(target_n)}")

    return key

def get_modulus_bytes_of_key(key_label: str) -> bytes:
    ''' get modulus bytes from key '''
    key = get_key_with_label(key_label)
    return get_modulus_bytes(key)


def sign_hash(key: object, digest_name: str, digest: bytes) -> bytes:
    ''' sign digest with key '''
    hash_algo = HASH_ALGO_NAMES[digest_name]()
    return key.sign(digest,
                    padding.PKCS1v15(),
                    utils.Prehashed(hash_algo))

def sign_hash_with_label(key_label: str,
                         digest_name: str,
                         digest: bytes) -> bytes:
    ''' sign digest with key identified by label '''
    key = get_key_with_label(key_label)
    return sign_hash(key, digest_name, digest)


def sign_hash_with_modulus(modulus: bytes,
                           digest_name: str,
                           digest: bytes) -> bytes:
    ''' sign digest with key identified by modulus '''
    key = get_key_with_modulus(modulus)
    return sign_hash(key, digest_name, digest)



########################################################################
#
# Operation with ESRP
#
########################################################################

###
# DER operations
#

def get_modulus_from_public_key_bytes(pub_info_der: bytes) -> bytes:
    ''' extract the modulus from the PUBLIC KEY ASN.1 structure (DER) '''
    pub_key = load_der_public_key(pub_info_der)

    if not pub_key.isinstance(pub_key,rsa.RSAPublicKey):
        raise ValueError("Not an RSA key")

    return get_modulus_bytes(pub_key)



###
# OpenSSL operations
# The ESRP engine is sometimes writing to stdout instead of stderr
# so unfortunately rule is to always use an -out argument (and a file)
# to capture the results instead of piping to stdout
#

def esrp_ossl_engine_do(args: list[str], stdin_input: object = None) -> bytes:
    ''' bottleneck routine for ossl cli command execution
    the name of the output file will be appended to the args
    result of the command will be returned as bytes or None if error
    '''
    # check token always in case ESRP server needs to be contacted
    check_token(ESRP_CONFIG_PATH)

    args.insert(0, OPENSSL_PATH)

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, 'output')
        args.append(out_path)
        subprocess.run(args,
                       input=stdin_input,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT,
                       check=True)
        # get modulus from public key
        with open(out_path, 'rb') as res_fd:
            return res_fd.read()

# NOTE: the PEM keys were actually generated manually from the
# CSR and are currently stored in the cert cache with the
# name CP-500<>-Key.pem. So we do not need OpenSSL
# engine to retrieve the public keys. But this is a
# workaround because the ESRP keys were created without
# certificates. The OpenSSL engine is able to retrieve
# the keys programmatically if there were added to
# certificates. So for the future, we keep the
# code here even though there's a simpler solution
# since this code works in all cases.

def esrp_get_public_key_aux(key_name: str, modulus_only: bool) -> bytes:
    ''' get ESRP key modulus '''
    the_args = ['pkey',
               '-in', f'KeyCode={key_name};' + FULL_CONFIG_STR,
               '-inform', 'engine',
               '-engine', 'esrp',
               '-pubout',
               '-outform', 'DER' if modulus_only else 'PEM',
               '-out']   # esrp_ossl_engine_do will add output name
    pub_info = esrp_ossl_engine_do(the_args)
    if modulus_only:
        return get_modulus_from_public_key_bytes(pub_info)

    return pub_info


def esrp_sign_hash_aux(key_name: str,
                       algo_name: str,
                       digest: bytes) -> bytes:
    ''' sign a digest '''
    the_args = ['pkeyutl',
                '-inkey', f'KeyCode={key_name};' + FULL_CONFIG_STR,
                '-keyform', 'engine',
                '-engine', 'esrp',
                '-pkeyopt', f'digest:{algo_name}',
                '-out']   # esrp_ossl_engine_do will add output name
    signature_der = esrp_ossl_engine_do(the_args, stdin_input=digest)
    return signature_der


def esrp_sign_hash_with_modulus_aux(modulus: bytes,
                                    algo_name: str,
                                    digest: bytes) -> bytes:
    ''' identify the key with the modulus and sign a digest '''
    for key_name in KEY_IN_CERTS:
        key_modulus = esrp_get_public_key_aux(key_name,
                                              modulus_only=True)
        if key_modulus == modulus:
            return esrp_sign_hash_aux(key_name, algo_name, digest)

    raise ValueError(f"No key found for the modulus {hex(modulus)}")



###
# ESRP
# exposed API
#


def esrp_get_public_key(key_set: int, key_label: str) -> bytes:
    ''' return the public key in PEM format '''

    # fpk4 special case: always use the (more protected) production key
    if key_label == 'fpk4':
        key_set = 1

    if key_set == 0:
        pub_key = get_public_key(get_key_with_label(key_label))
        return pub_key.public_bytes(encoding=Encoding.PEM,
                                    format=PublicFormat.SubjectPublicKeyInfo)

    if key_set == 1:
        key_name = KEY_MAPPING[key_label]
        return esrp_get_public_key_aux(key_name, modulus_only=False)

    raise ValueError(f"Invalid key set: {key_set}")


def esrp_get_modulus(key_set: int, key_label: str) -> bytes:
    ''' return the RSA modulus as bytes '''
    # fpk4 special case: always use the (more protected) production key
    if key_label == 'fpk4':
        key_set = 1

    if key_set == 0:
        return get_modulus_bytes_of_key(key_label)

    if key_set == 1:
        key_name = KEY_MAPPING[key_label]
        return esrp_get_public_key_aux(key_name, modulus_only=True)

    raise ValueError(f"Invalid key set: {key_set}")

def esrp_sign_hash_with_key(key_set: int,
                            key_label: str,
                            algo_name: str,
                            digest: bytes) -> bytes:
    ''' signs a digest using RSA PKCS1.5 '''

    # fpk4 special case: always use the (more protected) production key
    if key_label == 'fpk4':
        key_set = 1

    if key_set == 0:
        return sign_hash_with_label(key_label, algo_name, digest)

    if key_set == 1:
        key_name = KEY_MAPPING[key_label]
        return esrp_sign_hash_aux(key_name, algo_name, digest)

    raise ValueError(f"Invalid key set: {key_set}")


def esrp_sign_hash_with_modulus(key_set: int,
                                modulus: bytes,
                                algo_name: str,
                                digest: bytes) -> bytes:
    ''' signs a digest using RSA PKCS1.5 using the key with the modulus specified
    This is an infrequent operation and only with "customer" keys '''
    if key_set == 0:
        return sign_hash_with_modulus(modulus, algo_name, digest)

    if key_set == 1:
        return esrp_sign_hash_with_modulus_aux(modulus, algo_name, digest)

    raise ValueError(f"Invalid key set: {key_set}")


def esrp_signer_cert() -> str:
    ''' returns the ESRP signer certificate (check need for renewal) '''
    esrp_cfg = read_json(ESRP_CONFIG_PATH)

    # pass the password via pipe; otherwise might end up in some
    # error message (exception)
    args = [
        "openssl",  "pkcs12",  "-in",  esrp_cfg['RequestSignerPfxPath'],
        "-clcerts", "-nokeys",  "-passin", "fd:0"
    ]
    res = subprocess.run(args,
                         input=esrp_cfg['RequestSignerPfxPassword'],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
			 encoding='utf-8',
                         check=True)
    return res.stdout.encode('utf-8')
