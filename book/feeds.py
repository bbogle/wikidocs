# -*- coding: utf-8 -*-
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
import markdown

from book.models import Book

class BookFeed(Feed):

    def get_object(self, request, book_id):
        return get_object_or_404(Book, pk=book_id)

    def title(self, obj):
        return obj.subject

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return obj.summary

    def items(self, obj):
        return obj.recent_pages(limit=30)

    def item_title(self, item):
        return item.subject

    def item_description(self, item):
        extensions = ["tables", "toc", "footnotes", "fenced_code"]
        return mark_safe(markdown.markdown(force_unicode(item.content),
                                           extensions,
                                           safe_mode=True,
                                           enable_attributes=False))
