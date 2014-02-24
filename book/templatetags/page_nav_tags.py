# -*- coding: utf-8 -*-
from django import template
from book.models import Page

register = template.Library()

def get_first_page(book, isAuthor):
    if book.page_set.count() > 0:
        if isAuthor:
            result = book.page_set.order_by("seq")
        else:
            result = book.page_set.filter(open_yn='Y').order_by("seq")
        if result: return result[0]
    return ""


def get_prev_page(page, isAuthor):
    try:
        if isAuthor:
            return Page.objects.filter(book=page.book, seq__lte=page.seq-1).order_by("-seq")[0]
        else:
            return Page.objects.filter(book=page.book, seq__lte=page.seq-1, open_yn="Y").order_by("-seq")[0]
    except:
        return ""


def get_next_page(page, isAuthor):
    try:
        if isAuthor:
            return Page.objects.filter(book=page.book, seq__gte=page.seq+1).order_by("seq")[0]
        else:
            return Page.objects.filter(book=page.book, seq__gte=page.seq+1, open_yn="Y").order_by("seq")[0]
    except:
        return ""


@register.inclusion_tag('book/tags/prev_next.html')
def prev_next(request, page):
    isAuthor = request.user in page.book.user.all()
    prev = get_prev_page(page, isAuthor)
    next = get_next_page(page, isAuthor)
    return {
        "page":page,
        "prev":prev,
        "next":next,
    }

@register.inclusion_tag('book/tags/book_next.html')
def book_next(request, book):
    isAuthor = request.user in book.user.all()
    first_page = get_first_page(book, isAuthor)

    return {
        "first_page":first_page,
    }
