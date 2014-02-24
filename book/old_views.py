from django.http import HttpResponse
from django.shortcuts import redirect

import urllib
import urllib2


def api_page(request, no):
    data = urllib.urlencode({})
    header = {}
    req = urllib2.Request("http://old.wikidocs.net/api/page/%s" % no, data, header)  # POST request doesn't not work
    return HttpResponse(urllib2.urlopen(req).read())


def api_toc(request):
    pageid = request.POST["pageid"]
    data = urllib.urlencode({'pageid': pageid})
    header = {}
    req = urllib2.Request("http://old.wikidocs.net/api/toc", data, header)  # POST request doesn't not work
    return HttpResponse(urllib2.urlopen(req).read())


def api_comment(request):
    pageid = request.POST["pageid"]
    author = request.POST["author"]
    comment = request.POST["comment"]

    data = urllib.urlencode({'pageid': pageid, 'author':author, 'comment':comment})
    header = {}
    req = urllib2.Request("http://old.wikidocs.net/api/comment", data, header)  # POST request doesn't not work
    return HttpResponse(urllib2.urlopen(req).read())