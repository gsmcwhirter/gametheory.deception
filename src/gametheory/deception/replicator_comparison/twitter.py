import urllib
import httplib
import base64

def _urlencode(h):
    rv = []
    for k,v in h.iteritems():
        rv.append('%s=%s' %
            (urllib.quote(k.encode("utf-8")),
            urllib.quote(v.encode("utf-8"))))
    return '&'.join(rv)

def _makeAuthHeader(user, passwd, headers={}):
    authorization = base64.encodestring('%s:%s'
        % (user, passwd))[:-1]
    headers['Authorization'] = "Basic %s" % authorization
    return headers

def cb(x):
    print "Posted id", x

def eb(e):
    print e

def tweet(message, at=None):
    if at is not None:
        message = "@%s %s" % (at, message)
    
    client = httplib.HTTPConnection('identi.ca')
    client.connect()
    client.request('POST','/api/statuses/update.xml',_urlencode({"status": message}),_makeAuthHeader('lpssimcomp','UC1LPS1zk00l!',{'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'}))
    response = client.getresponse()
    response_text = response.read()
    response_status = response.status
    client.close()
    
    print response_status
    
    
