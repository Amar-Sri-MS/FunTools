########################################################
#
# test_boot_step_server.py
#
# Copyright (c) Microsoft Corporation. 2023
#
########################################################


import argparse
import requests
import traceback
import warnings
import urllib3

CGI_SCRIPT='enrollment_boot_step.cgi'

# version string, list of enrollment boot steps, total bootsteps
# first is before bootsteps in interface.json
# second is before ROM enrollment
# third is after ROM enrollnent
TEST_VERSIONS=(
    ('bld_133661-fc9640b7fdb9', (0x68,), 50),
    ('bld_133661-f472c2db4', (0x5C,), 48),
    ('bld_133661-4e45bce140163', (0x48,0x70), 51)
    )

def boot_step_vals(server_reply):
    return [int(val,0) for val in server_reply.split(",")]

def boot_step_request(server, version, bootstep, tls_verify):

    url_str = "https://" + server + "/cgi-bin/" + CGI_SCRIPT

    response = requests.get(url_str,
                            params={'version': version, 'bootstep':bootstep},
                            verify=tls_verify)

    return response.text


def test_enrollment_bootsteps(server, tls_verify):

    errors = 0

    ''' old reply returns only the last enrollment boot step '''
    for ver_info in TEST_VERSIONS:
        old_reply = boot_step_request(server, ver_info[0], "", tls_verify)
        old_bootsteps = boot_step_vals(old_reply)
        new_reply = boot_step_request(server, ver_info[0], "enrollment", tls_verify)
        new_bootsteps = boot_step_vals(new_reply)

        ver_errors = 0
        # old reply should have only one bootstep
        if len(old_bootsteps) != 1:
            ver_errors += 1
        if len(old_bootsteps) == 0:
            continue

        # last element of new reply should be old bootstep
        if new_bootsteps[-1] != old_bootsteps[0]:
            print(f"{new_bootsteps[-1]} != {old_bootsteps[0]}")
            ver_errors += 1

        # new bootsteps should match the expected list
        if tuple(new_bootsteps) != ver_info[1]:
            ver_errors += 1

        if ver_errors:
            print(f"{ver_errors} error for \"{ver_info[0]}\"")
            print(f"reply (old): {old_reply}")
            print(f"reply (new): {new_reply}")
            errors += ver_errors

    return errors


def test_all_bootsteps(server, tls_verify):

    errors = 0

    ''' old reply returns only the last enrollment boot step '''
    for ver_info in TEST_VERSIONS:
        new_reply = boot_step_request(server, ver_info[0], "all", tls_verify)
        vals = []
        for l in new_reply.splitlines():
            vals.append(l.split(","))

        ver_errors = 0
        total = len(vals)

        if total != ver_info[2]:
            print(f"got {total} vals for {ver_info[0]} expected {ver_info[2]}")
            ver_errors += 1

        # verify sorted
        sorted = all(int(vals[i][0],0) <= int(vals[i+1][0], 0)
                     for i in range(total-1))
        if not sorted:
            print(f"all for {ver_info} is not sorted")
            ver_errors += 1

        if ver_errors:
            print(vals)
            errors += ver_errors

    return errors


def main_program():

    errors = 0

    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--server", dest="server",
                        default="f1reg.fungible.com",
                        help="Ip address or DNS name of server to test")

    options = parser.parse_args()

    tls_verify = True if options.server == "f1reg.fungible.com" else False

    if not tls_verify:
        warnings.simplefilter('ignore',
                              category=urllib3.exceptions.InsecureRequestWarning)

    try:
        errors += test_enrollment_bootsteps(options.server, tls_verify)

        errors += test_all_bootsteps(options.server, tls_verify)

    except Exception as ex:
        traceback.print_exc()
        errors += 1

    print("Test completed on server %s with %d errors" % (options.server, errors))


if __name__=="__main__":
    main_program()
