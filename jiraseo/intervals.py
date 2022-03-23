#!/usr/local/bin/python3 -u

## Jira's JQL is pretty lousy. This script uses the JIRA REST API to
## try and do some more useful things. Specifically, display jiras
## in upcoming sprints and also jiras that should be assigned to sprints
## but are not.
##
## Experimentation command:
## jirashell -u $USER -P -v latest -s http://jira.fungible.local:80
##
##

from typing import List, Set, Dict, Tuple, Optional, Any
import jira # type: ignore
import sys
import datetime
import getpass

# TODO: argparse
uname = None
NSPRINTS = 8
JIRA_SERVER = "http://jira.fungible.local:80"

# list of milestones that _don't_ need sprints assigned
UNSCHEDULED_MILESTONES = ["release 3.0", "later"]

# master jira object
jconn : Any = None


###
##  Error handling
#
class QueryError(Exception):
    def __init__(self, err: str) -> None:
        self.error = err    


###
##  sprint number computations
#

SPRINT0 = 80
SPRINT0_DATE = datetime.date(2020, 5, 25)
SPRINT_LEN = datetime.timedelta(days=14)
SPRINT_WD_LEN = datetime.timedelta(days=10)
SPRINT_FMT = "SW Sprint {sprint} [{start.month}/{start.day} - {end.month}/{end.day}]"
SPRINT_OFFSET = 12

def sprint_for_date(date: datetime.date) -> int:
    assert(date >= SPRINT0_DATE)

    ddelta = (date - SPRINT0_DATE).days
    sdelta = int(ddelta / SPRINT_LEN.days)

    return SPRINT0+sdelta
    

def current_sprint() -> int:
    return sprint_for_date(datetime.date.today())

def date_for_sprint_start(sprint: int) -> datetime.date:
    sdelta = sprint - SPRINT0
    ddelta = sdelta * SPRINT_LEN.days
    return SPRINT0_DATE + datetime.timedelta(days=ddelta)

def date_for_sprint_end(sprint: int) -> datetime.date:
    return date_for_sprint_start(sprint) + SPRINT_LEN - datetime.timedelta(days=1)

def sprint_as_str(sprint: int) -> str:
    start = date_for_sprint_start(sprint)
    end = date_for_sprint_end(sprint)
    return SPRINT_FMT.format(sprint=sprint, start=start, end=end)
    
###
##  printing
#

def print_issue(issue):
    url = "%s/browse/%s" % (JIRA_SERVER, issue.key)
    # print("* [%s](%s): %s" % (str(issue.key).lower(), url, issue.fields.summary))
    print("%s: %s (%s)" % (str(issue.key).lower(), issue.fields.summary, url))

###
##  jira query a sprint
#

def jira_list_for_sprint(sprint: int) -> List[Any]:

    global jconn
    sq = "resolution = Unresolved AND Sprint = %s AND assignee in (currentUser())" % (sprint + SPRINT_OFFSET)

    # query it
    try:
        issues = jconn.search_issues(sq)
    except jira.exceptions.JIRAError as jerr:
        raise QueryError(jerr.text)
        

    return issues

def find_jira_list_without_sprint() -> List[Any]:
    
    global jconn

    # make the exclusion list
    exclu = ", ".join([ '"%s"' % x for x in UNSCHEDULED_MILESTONES ])

    # make the full query
    sq = "sprint is EMPTY AND assignee = currentuser() AND resolution is EMPTY AND fixVersion not in (%s)" % exclu

    # query it
    issues = jconn.search_issues(sq, maxResults=1000)

    return issues

###
##  Main code
#

def main() -> None:

    global jconn
    
    # read a line of stdin
    sys.stdout.write("Jira Username: ");
    sys.stdout.flush()
    uname = sys.stdin.readline().strip()
    passwd = getpass.getpass("Password for %s:" % uname) 

    # do the authentication
    print("connecting")
    try:
        jconn = jira.JIRA(JIRA_SERVER, auth=(uname, passwd))
    except:
        print("Failed to authenticate to jira")
        sys.exit(1)

    print("connected")

    jvector = []

    ### Print out all the upcoming sprints
    cur = current_sprint()
    print(cur)
    for sprint in range(cur, cur+NSPRINTS):

        error = None
        try:
            jlist = jira_list_for_sprint(sprint)
        except QueryError as err:
            error = err

        if (error is None):
            jvector.append(len(jlist))
            print("\n== %s [%d] ==" % (sprint_as_str(sprint), len(jlist)))
    
            for issue in jlist:
                print_issue(issue)
        else:
            print("\n== %s [error] ==" % sprint_as_str(sprint))
            print(error)
            
        print()
    
    ### Print out all the jiras that don't have sprints
    jlist = find_jira_list_without_sprint()
    print("\n= %s [%d] ==" % ("Jiras that need a sprint assigned", len(jlist)))
    jvector.append(len(jlist))
    for issue in jlist:
        print_issue(issue)
    print()


    ### Print out the distribution and totals
    tjiras = sum(jvector)
    nsprints =len(jvector) - 1
    jsprint = float(tjiras) / nsprints
    jday = jsprint / SPRINT_WD_LEN.days
    
    print("\n== Summary ==")
    print("Distribution by count: %s" % jvector)
    print("Total jira commitment: %d" % tjiras)
    print("Ideal jiras/sprint:    %.1f" % jsprint)
    print("Goal jiras/wkday:      %.1f" % jday)


###
##  entrypoint
#
if (__name__ == "__main__"):
    main()
