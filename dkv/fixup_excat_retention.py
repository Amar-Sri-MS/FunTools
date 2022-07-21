#!/usr/bin/env python3

#
# Sets retention tags on objects that do not have such tags.
#


import argparse
import logging
import os
import requests
import sys
import time

script_path = os.path.join(os.path.dirname(__file__), "../scripts")
print(script_path)
sys.path.append(script_path)
import s3util


# Global arguments
args = None
host = "cgray-vm0:9000"
dkv_excat_url = "http://cgray-vm0/dkv/buckets/excat"

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-k", "--key", action="store", default=None)
    parser.add_argument("-s", "--secret", action="store", default=None)
    parser.add_argument(
        "--sure", action="store_true", help="Perform the fix-up actions"
    )
    parser.add_argument("--token", default=None)
    parser.add_argument("--bucket", default="excat")

    global args
    args = parser.parse_args()

    token = args.token
    count = 0
    while True:
        log.info("Count: %d from token %s" % (count, token))
        token, objs = s3util.list_bucket(
            host, args.bucket, args.key, args.secret, token, 100
        )

        for obj in objs:
            if obj.endswith(".json"):
                continue

            tags = s3util.get_tags(obj, host, args.bucket, args.key, args.secret, None)
            if "retention" not in tags:
                set_retention(obj)
            else:
                if not args.sure:
                    log.info("(dryrun) %s: skipping" % obj)
            count += 1

        if not token:
            print("All done")
            break

        # TODO(jimmy): do we need some form of rate-limiting here?
        time.sleep(1)


def set_retention(obj):
    """Sets a retention length on the object and its metadata"""
    retention = determine_retention_from_metadata(obj)

    if args.sure:
        s3util.set_tags(
            obj,
            host,
            args.bucket,
            args.key,
            args.secret,
            None,
            {"retention": retention},
        )

        mdblob = obj.replace(".bz", ".json")
        mdret = "forever" if retention in ["archive", "forever"] else "archive"
        s3util.set_tags(
            mdblob, host, args.bucket, args.key, args.secret, None, {"retention": mdret}
        )

        log.info("%s: retention ==> %s" % (obj, retention))
    else:
        log.info("(dryrun) %s: retention ==> %s" % (obj, retention))


def determine_retention_from_metadata(obj):
    """
    Determines retention length from json metadata. Returns None if a
    retention length could not be determined.
    """
    mdblob = obj.replace(".bz", ".json")
    path = "%s/%s" % (dkv_excat_url, mdblob)
    resp = requests.get(path)

    if resp.status_code == requests.codes.ok:
        js = resp.json()
        bldname = js.get("fname", "")
        return determine_retention_from_bldname(bldname, obj)

    return None


SDK_PRESERVE = ["rel_", "patch_", "poc_"]


def determine_retention_from_bldname(bldname, obj):
    """
    Determine retention length from original path during the build.
    Cribbed from previous cleanup script.
    """
    if bldname.startswith("/data/jenkins/ws/funsdk/"):
        parts = bldname.split(os.sep)
        if parts[0] == "":
            del parts[0]
        if parts[4] == "pull_requests":
            return "short"
        if parts[4] == "master":
            # no easy way to tell which ones were "released"
            return "forever"
        if parts[4] == "funsdk_on_demand":
            return "medium"
        if parts[4] == "funos_on_demand":
            return "medium"

        for pref in SDK_PRESERVE:
            if parts[4].startswith(pref):
                # no easy way to tell which ones were "released"
                return "forever"

        # other SDK
        return "medium"

    if bldname.startswith("/data/jenkins/ws/integration/"):
        return "medium"
    if bldname.startswith("/data/jenkins/ws/emulation/"):
        return "medium"

    # unknown path
    log.warning("Unknown build path %s for %s" % (bldname, obj))
    return "medium"


if __name__ == "__main__":
    main()
