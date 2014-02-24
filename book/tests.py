# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test.client import Client
from models import Book, Page, Sell


class DocTest(TestCase):
    def test_docs_list(self):
        book1 = Book(subject="Jump to python", open_yn="Y")
        book1.save()
        book2 = Book(subject="Wang chobo", open_yn="Y")
        book2.save()

        Sell(book=book1).save()
        Sell(book=book2).save()

        c = Client()
        response = c.get("")
        sells = response.context["sells"]
        self.assertEquals(2, len(sells))

        self.assertTrue("Jump to python" in response.content)
        self.assertTrue("Wang chobo" in response.content)


    def test_page_parents(self):
        book = Book(subject="Jump to python")
        book.save()

        p1 = Page(subject="p1", content="..", book=book)
        p1.save()
        p2 = Page(subject="p2", content="..", book=book, parent=p1)
        p2.save()
        p3 = Page(subject="p3", content="..", book=book, parent=p2)
        p3.save()
        p4 = Page(subject="p4", content="..", book=book, parent=p2)
        p4.save()

        self.assertFalse(p1.get_parents())
        self.assertTrue(p1 in p2.get_parents())
        self.assertTrue(p1 in p3.get_parents())
        self.assertTrue(p2 in p3.get_parents())
        self.assertTrue(p1 in p4.get_parents())
