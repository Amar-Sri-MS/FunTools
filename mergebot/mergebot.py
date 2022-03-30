#!/usr/bin/env python3

import os
from github import Github

ORGS = ["fungible-inc"]
TEST_ALL = False
if (TEST_ALL):
    MERGEBOT_TOPIC = None
    MERGEBOT_PREFIX = ""
else:
    MERGEBOT_TOPIC = "f1"
    MERGEBOT_PREFIX = "mergebot:"

def check_pr(repo, pr):

    reviewed_ok = False
    checks_ok = False
    mergeable_ok = False
    changes_requested = False
    bad = False
    
    print(pr)
    print("\t%s" % pr.html_url)
    if (not pr.title.startswith(MERGEBOT_PREFIX)):
        print("\tPR not for mergebot")
        return
    
    x = pr.head.sha
    print("\tref: %s" % x)
    z = repo.get_commit(x)
    status = z.get_combined_status()
    print("\tstatus: %s (%s) %s" % (status, status.state, status.statuses))
    if ((len(status.statuses) == 0) or (status.state == "success")):
        checks_ok = True
    print("\tmerge: %s %s" % (pr.mergeable, pr.mergeable_state))
    if ((pr.mergeable == True) and (pr.mergeable_state != "clean")):
        mergeable_ok = True
    rs = pr.get_reviews()
    for r in rs:
        print("\t%s (%s)" % (r, r.state))
        if (r.state == "CHANGES_REQUESTED"):
            changes_requested = True
        if (r.state == "APPROVED"):
            reviewed_ok = True

    if (not checks_ok):
        print("\tChecks failed, cannot merge")
        bad = True
    if (not mergeable_ok):
        print("\Merge blocked / denied")
        bad = True
    if (changes_requested):
        print("\tChanges requested, cannot merge")
        bad = True
    if (not reviewed_ok):
        print("\tNo approvals, cannot merge")
        bad = True

    if (bad):
        print("\tChecks failed. Not merging")
        return
    
    print("\tmergebot is merging!")
    pr.merge("PR merge attempt by mergebot")

def scan_repo(repo):

    print("Checking %s" % repo.name)
    topics = repo.get_topics()

    if (MERGEBOT_TOPIC is not None):
        for topic in topics:
            if (topic == MERGEBOT_TOPIC):
                break
        else:
            print("\tNot a mergebot repo")
            return
    
    # check it
    prs = repo.get_pulls(state='open')
    for pr in prs:
        check_pr(repo, pr)
    

def scan_orgs(g, orgs):
    for orgname in orgs:
        print("Checking org %s" % orgname)
        org = g.get_organization(orgname)

        for repo in org.get_repos():
            scan_repo(repo)

def main():
    # First create a Github instance  using an access token
    token = open(os.path.expanduser("~/.github-token")).readline().strip()
    g = Github(token)

    try:
        scan_orgs(g, ORGS)
    except KeyboardInterrupt:
        print("Cancelled by user")
    except:
        raise

    
if (__name__ == "__main__"):

    main()
