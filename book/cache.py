# -*- coding: utf-8 -*-
import os
import sys

HOME = "/home/pahkey/project/wikidocs"
sys.path.insert(0, HOME)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wikidocs.settings")

from django.conf import settings
from django.core.cache import cache
from book.models import Page

def get_prefix(request):
    if request.mobile: return "mobile."
    else: return "normal."


def cache_get(request, _id):
    if not settings.CACHE_USE: return ""
    # login user can't use cache
    if request.user.is_authenticated(): return ""
    prefix = get_prefix(request)
    _id = prefix+_id
    return cache.get(_id)


def cache_put(request, _id, data):
    if not settings.CACHE_USE: return
    # login user can't use cache
    if request.user.is_authenticated(): return ""

    prefix = get_prefix(request)
    _id = prefix+_id
    cache.set(_id, data, settings.CACHE_TIMEOUT)


def cache_remove(_id):
    for prefix in ["mobile.", "normal."]:
        cache.delete(prefix+str(_id))
    # cache_remove_list()


def cache_clear(book):
    cache_remove("book_%s" % book.id)
    for item in Page.objects.filter(book=book).values("id"):
        cache_remove(item.get("id"))


def cache_clear_all():
    cache.clear()
    print "cache cleared."


if __name__ == "__main__":
    opt = sys.argv[1]
    if opt == "clearall":
        cache_clear_all()
