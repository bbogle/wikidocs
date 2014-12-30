# -*- coding: utf-8 -*-
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404

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

    def item_pubdate(self, item):
        return item.modify_time