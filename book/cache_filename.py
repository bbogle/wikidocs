from django.shortcuts import render
from book.models import Page
from wikidocs import settings

import os


def get_cache_filename(isMobile, _id):
    if isMobile:
        return settings.CACHE_DIR+"/mble/{0}.cache".format(_id)
    else:
        return settings.CACHE_DIR+"/anon/{0}.cache".format(_id)

    # if isLogined:
    #     return settings.CACHE_DIR+"/user/{0}.cache".format(_id)
    # else:
    #     return settings.CACHE_DIR+"/anon/{0}.cache".format(_id)


def cache_get(request, _id):
    if not settings.CACHE_USE: return ""

    # login user can't use cache
    if request.user.is_authenticated(): return ""

    filename = get_cache_filename(request.mobile, _id)
    if os.path.exists(filename):
        f = open(filename)
        result = f.read()
        f.close()
        return result
    else:
        return ""


def cache_put(request, _id, data):
    if not settings.CACHE_USE: return

    # login user can't use cache
    if request.user.is_authenticated(): return ""

    filename = get_cache_filename(request.mobile, _id)
    _dirname = os.path.dirname(filename)
    if not os.path.exists(_dirname): os.makedirs(_dirname)
    f = open(filename, 'w')
    f.write(data)
    f.close()


def cache_remove(_id):
    mble_filename = get_cache_filename(True, _id)
    anon_filename = get_cache_filename(False, _id)
    if os.path.exists(mble_filename): os.remove(mble_filename)
    if os.path.exists(anon_filename): os.remove(anon_filename)


def cache_clear(book):
    cache_remove("book_%s" % book.id)
    for item in Page.objects.filter(book=book).values("id"):
        cache_remove(item.get("id"))


# def make_cache(request, book):
#     toc = Page.objects.filter(book=book).order_by("seq")
#     for page in toc:
#         context = {"page": page, "toc": toc}
#         result = render(request, 'book/page.html', context)
#         cache_put(True, page.id, result.content)