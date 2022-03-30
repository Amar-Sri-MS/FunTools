#!/usr/local/bin/python -u

## Jira's JQL is pretty lousy. This script uses the JIRA REST API to
## try and do some more useful things. Specifically, scrape the
## previous work week's activity in jira for a snippet
##
## Experimentation command:
## jirashell -u $USER -P -v latest -s http://jira.fungible.local:80
##
##

from jira import JIRA
import sys
import datetime
import getpass

# TODO: argparse
uname = None 

###
##  Functions
#

def filter_on_history(jira, issues, start_date, end_date):

    filtered = []
    global uname
    
    # print("Filtering %d issues" % len(issues))
    for issue in issues:
        # scan the changelog for changes by me
        for h in issue.changelog.histories:
            if (h.author.key != uname):
                continue

            # get its date
            dt = datetime.datetime.strptime(h.created.split('T')[0], '%Y-%m-%d').date()
            if (dt < start_date):
                continue
            if (dt > end_date):
                continue

            # append and continue
            filtered.append(issue)
            break

    return filtered

def pri(issue):
    url = "http://jira.fungible.local:80/browse/%s" % issue.key
    print("* [%s](%s): %s" % (str(issue.key).lower(), url, issue.fields.summary))


###
##  Main code
#

# read a line of stdin
sys.stdout.write("Jira Username: ");
sys.stdout.flush()
uname = sys.stdin.readline().strip()
passwd = getpass.getpass("Password for %s:" % uname) 

# do the authentication
print("connecting")
try:
    jira = JIRA('http://jira.fungible.local:80',
                     auth=(uname, passwd))
except:
    print("Failed to authenticate to jira")
    sys.exit(1)
    
print("connected")
#print(jira)

## Work out the date range
today = datetime.date.today()
# monday -1wk
delta_mon = datetime.timedelta(days=datetime.date.today().weekday(), weeks=1)
start_date_d = datetime.date.today() - delta_mon
end_date_d = start_date_d + datetime.timedelta(6) # +6 for Sunday
end_next_d = start_date_d + datetime.timedelta(7) # +7 for Monday

# make them text
start_date = start_date_d.isoformat()
end_date = end_date_d.isoformat()
end_next = end_next_d.isoformat()

## Queries:

# Snippets list
# 1) All the jiras I created in the last week
#   (reporter = currentUser() OR creator = currentUser()) AND createdDate >= START_DATE AND createdDate <= END_DATE
#
# 2) All the jiras I closed in the last week
#   a. resolved >= START_DATE and resolved <= END_DATE
#   b. scan for ...?
#
# 3) All the jiras I modified in the last week
#   a. modified >= START_DATE
#   b. scan for activity by me >= START_DATE

print("JIRA activity for dates %s -> %s" % (start_date, end_date))
print("") # Blank line for markdown formatting

### Issues I created in the last week

# make a query
sq = "(reporter = currentUser() OR creator = currentUser()) AND createdDate >= %s AND createdDate <= %s" % (start_date, end_date)

# query it
issues = jira.search_issues(sq)

# log it
print("Created issues (%d)" % len(issues))
for issue in issues:
    pri(issue)
print()

sys.stdout.flush()

### Issues I resolved in the last week

sq = 'status changed to Closed by currentUser() DURING ("%s","%s")  OR status changed to Resolved by currentUser() during ("%s", "%s")' % (start_date, end_next_d, start_date, end_next)


# query it
issues = jira.search_issues(sq)

# log it
print("Resolved issues (%d)" % len(issues))
for issue in issues:
    pri(issue)
print()

sys.stdout.flush()

### Issues I modified in the last week

# ... start with issues modified in the last week I ever looked at
sq = 'updated >= "%s" and updated <= "%s" and lastviewed is not empty' % (start_date, end_date)

# print(sq)

# query it
issues = jira.search_issues(sq, expand="changelog")

# now filter it
issues = filter_on_history(jira, issues, start_date_d, end_date_d)

# log it
print("Modified issues (%d)" % len(issues))
for issue in issues:
    pri(issue)



