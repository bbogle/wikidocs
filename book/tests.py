# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test.client import Client
from models import Book, Page, Sell

from django.contrib.auth.models import User


class DocTest(TestCase):
    def test_docs_list(self):
        u1 = User.objects.create_user("pahkey@gmail.com", "pahkey@gmail.com", "1")
        u1.save()


        book1 = Book(subject="Jump to python", open_yn="Y", creator=u1)
        book1.save()


    def xtest_page_parents(self):
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
