import sys
import os
if os.path.exists("/home/cgray/dkv/FunTools/scripts"):
    # for deployment
    sys.path.append("/home/cgray/dkv/FunTools/scripts")
else:
    # for development
    ws = os.environ.get('WORKSPACE')
    if ws:
        sys.path.append(os.path.join(ws, 'FunTools', 'scripts'))
import s3util
import requests
import xml
import time
import flask
import werkzeug
import tempfile
import humanize
import datetime
import urllib.parse
import traceback
import netrc
import xml.etree.ElementTree as xmlt

APP_ROOT = os.path.dirname(__file__)

app = flask.Flask("dkv",
                  static_folder=os.path.join(APP_ROOT, "static"),
                  template_folder=os.path.join(APP_ROOT, "templates"))

MINIO_SERVER = "cgray-vm0:9000"
MINIO_ROOT_GET = 'http://%s/' % MINIO_SERVER


def AWSNS(tag):
    return "{http://s3.amazonaws.com/doc/2006-03-01/}" + tag

@app.route("/")
def home():
    return app.send_static_file("index.html")

@app.route("/debug")
def debug():
    return os.getcwd()


def bucket_redir(path):
    # just redirect to the download location
    url = os.path.join(MINIO_ROOT_GET, path)
    return flask.redirect(url, code=302)

def removeprefix(s, pref):
    if (s.startswith(pref)):
        s = s[len(pref):]
    return s

def removesuffix(s, suf):
    if (s.endswith(suf)):
        s = s[:-len(suf)]
    return s

def readable_timedelta(s):
    modtime = datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ")
    modtime = modtime.replace(tzinfo=datetime.timezone.utc)
    return humanize.naturaldelta(datetime.datetime.now(datetime.timezone.utc)-modtime)

def query_expiration(url):

    # head request the URL
    hdrs = requests.head(url)

    exp = hdrs.headers.get("x-amz-expiration")
    if (exp is None):
        return ""

    try:
        start = exp.find('expiry-date=\"')
        exp = exp[start:]
        exp = removeprefix(exp, 'expiry-date=\"')
        end = exp.find('"')
        exp = exp[:end-1]
        exp = removesuffix(exp,  "00:00:00 GM")
    except:
        exp = ""
    
    return exp

def bucket_list(bucket, req_prefix, debug):

    # grab the filer
    url = os.path.join(MINIO_ROOT_GET, bucket)
    url += "?delimiter=/&prefix=%s" % req_prefix
    debug['minio_url'] = url
    r = requests.get(url, allow_redirects=True)

    if (r.status_code != requests.codes.ok):
        return ("%s\n" % str(debug)).encode() + r.content, r.status_code

    lbr = xmlt.fromstring(r.content)
    name = lbr.find(AWSNS("Name")).text
    prefix = lbr.find(AWSNS("Prefix")).text

    debug['prefix'] = prefix
    if (prefix is None):
        prefix = ""
    
    d = {}
    d['name'] = name
    d['keys'] = []

    # build the path list
    pathlist = []
    
    # add a "bucket root" node
    v = {}
    curpath = "/dkv/buckets/%s/" % name
    v['key'] = name
    v['url'] = curpath
    pathlist.append(v)

    # add a ".." node
    if (prefix != ""):
        pelms = prefix.split("/")[:-1]
        for pelm in pelms:
            v = {}
            v['key'] = pelm
            v['url'] = curpath
            curpath += "%s/" % pelm
            pathlist.append(v)

    d['pathlist'] = pathlist
    debug['pathlist'] = pathlist
            
    for elem in lbr.iter():
        v = {}
        if (elem.tag == AWSNS("Contents")):
            key = elem.find(AWSNS("Key")).text
            key = removeprefix(key, prefix)
            v['key'] = key
            v['url'] = os.path.join(MINIO_ROOT_GET, bucket, prefix, key)
            v['size'] = elem.find(AWSNS("Size")).text
            v['lastmod'] = elem.find(AWSNS("LastModified")).text
            v['lastmod_rel'] = readable_timedelta(v['lastmod']) + " ago"
            # v['expiration'] =  "in " + readable_timedelta(query_expiration(v['url']))
            v['expiration'] =  query_expiration(v['url'])
            d['keys'].append(v)

        if (elem.tag == AWSNS("CommonPrefixes")):
            for cp in elem.iter():
                if (elem.tag != AWSNS("Prefix")):
                    continue
            key = removeprefix(cp.text, prefix)
            v['key'] = key
            v['url'] = key
            d['keys'].append(v)

    if (debug['enabled']):
        d['debug'] = str(debug)
    else:
        d['debug'] = ''

    return flask.render_template("dirlist.html", **d)
    
    
@app.route('/buckets/<path:path>')
def bucket_get(path):
    # GET path

    debug = {}
    debug['enabled'] = False
    debug['path'] = path
    
    # single element
    if ('/' not in path):
        # add a / so relative links work
        return flask.redirect(path+"/", code=302)

    # is a path
    if (path[-1] == '/'):
        toks = path.split("/")
        if (toks[-1] == ''):
            toks = toks[:-1]
        debug['pathtoks'] = toks
        prefix = ""
        if (len(toks) > 1):
            prefix = os.path.join(*toks[1:]) + "/"
        return bucket_list(toks[0], prefix, debug)

    # anything else, assume it's / they want a raw file
    return bucket_redir(path)

@app.route('/buckets/<path:path>', methods=['POST'])
def bucket_put(path):
    # POST path
    # Each uploaded file creates a new URI based on the path route.

    upfiles = flask.request.files
    uplist = []

    nrc = netrc.netrc()
    (excat_user, _, excat_pass) = nrc.authenticators(MINIO_SERVER)

    for upkey in upfiles:
        upfile = upfiles[upkey]
        if upfile.filename == '':
            raise RuntimeException("Uploaded empty filename??")
        # sanitise the name
        fname = werkzeug.utils.secure_filename(upfile.filename)
        # save it to a temp filename
        fl = tempfile.TemporaryFile()

        # save it
        upfile.save(fl)

        # shuffle the names
        pelems = path.split("/")
        bucket = pelems[0]
        remname = os.path.join(*pelems[1:])
        remname = os.path.join(remname, fname)

        tags = determine_tags(bucket, fname)
        tags_header = None
        if tags:
            tags_header = urllib.parse.urlencode(tags)

        #if (True):
        #    return "remname %s buckets %s" % (path, bucket)
    
        # run the s3 upload
        fl.seek(0)
        s3util.upload_file_handle(fname, MINIO_SERVER, bucket, fl,
                                  content_type=upfile.content_type,
                                  remote_name=remname,
                                  key=excat_user,
                                  secret=excat_pass,
                                  tags=tags_header)

        uplist.append((bucket, remname))

    return "bucket put: %s/%s" % (path, uplist)


def determine_tags(bucket, fname):
    form_data = flask.request.form
    retention = form_data.get("retention")
    if (retention is None):
        # Default for legacy clients that do not provide retention information
        return None

    # validate the retention period is legit
    if (retention not in ["short", "medium", "long", "archive", "forever"]):
        flask.abort(400, "unknown retention period %s" % retention)

    tags = {"retention": retention}
    return tags


@app.route('/buckets/<path:path>', methods=['PUT'])
def tag_put(path):
    # PUT path for a specific URI, currently used for tagging

    nrc = netrc.netrc()
    (excat_user, _, excat_pass) = nrc.authenticators(MINIO_SERVER)

    change_retention = flask.request.args.get("retention")
    if (change_retention is None):
        flask.abort(404, "unsupported put request, add query ?retention=")

    # extract the bucket and resource name from the path
    pelems = path.split("/")
    bucket = pelems[0]
    remname = os.path.join(*pelems[1:])

    tags = determine_tags(None, None)
    s3util.set_tags(remname, MINIO_SERVER, bucket,
                    key=excat_user, secret=excat_pass, region=None, tags=tags)
    return "retention put: %s %s" % (remname, str(tags))


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    print("catching all!")
    return "catch_all"

@app.errorhandler(requests.exceptions.HTTPError)
def handle_http_error(e):
    """ Deal with http errors when making requests """
    return "%s\n" % (traceback.format_exc()), e.response.status_code

@app.errorhandler(Exception)
def handle_exception(e):
    # now you're handling non-HTTP exceptions only
    return "dkv server exception:\npath: %s\n%s" % (traceback.format_exc(), os.getcwd()), 500

# for wsgi
def application(env, start_response):
    """
    A basic WSGI application
    """

    #print(env)
    return app(env, start_response)
