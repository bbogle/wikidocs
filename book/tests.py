# -*- coding: utf-8 -*-
from django.core.urlresolvers import resolve

from django.test import TestCase
from django.contrib.auth.models import User

from models import Book, Page, Buy, Sell
from book.views import index

class HomePageTest(TestCase):
    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, index)


class BuyBookTest(TestCase):
    def create_book(self, subject):
        u1 = User.objects.create_user("pahkey@gmail.com", "pahkey@gmail.com", "1")
        u1.save()
        book = Book(subject=subject, creator=u1)
        book.save()
        return book

    def test_saving_a_POST_request(self):
        book = self.create_book("Jump To Python")
        sell = Sell(book=book, price=100, filename="jumptopython")
        sell.save()

        response = self.client.post(
            '/buy/save',
            data={
                'book_id': book.id,
                'buyer': "Hong",
                'email': 'test@test.com',
                'telno': '000-0000-0000',
                'agree': True,
            }
        )

        buy = Buy.objects.first()
        self.assertEquals(book, buy.book)
        self.assertTemplateUsed(response, 'book/buy_save.html')


class DocTest(TestCase):
    def test_docs_list(self):
        u1 = User.objects.create_user("pahkey@gmail.com", "pahkey@gmail.com", "1")
        u1.save()
        book1 = Book(subject="Jump to python", open_yn="Y", creator=u1)
        book1.save()


    def test_page_parents(self):
        u1 = User.objects.create_user("pahkey@gmail.com", "pahkey@gmail.com", "1")
        u1.save()
        book = Book(subject="Jump to python", creator=u1)
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
