# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.html import format_html

import datetime
import os


class Ip(models.Model):
    ip = models.CharField(max_length=30, unique=True, db_index=True)

    def __unicode__(self):
        return self.ip


OPEN_YN_CHOICES = (
    ("Y", u"공개"),
    ("N", u"비공개"),
)
ADV_YN_CHOICES = (
    ("Y", u"예"),
    ("N", u"아니오"),
)
CCL_LEFT = (
    ("by", u"예"),
    ("by-nc", u"아니오"),
)
CCL_RIGHT = (
    ("-", u"예"),
    ("-sa", u"동일한 이용허락조건을 적용하는 경우에만"),
    ("-nd", u"아니오"),
)
class Book(models.Model):
    user = models.ManyToManyField(User, verbose_name=u"저자")
    creator = models.ForeignKey(User, related_name="book_creator", verbose_name=u"지은이")
    subject = models.CharField(max_length=100, verbose_name=u"책 제목")
    create_time = models.DateTimeField(default=datetime.datetime.now)
    modify_time = models.DateTimeField(default=datetime.datetime.now)
    viewer = models.ManyToManyField(Ip, null=True, related_name="book_viewer")
    recommend = models.ManyToManyField(Ip, null=True, related_name="book_recommend")
    open_yn = models.CharField(max_length=1, default="N", choices=OPEN_YN_CHOICES, verbose_name=u"공개/비공개")
    image = models.ImageField(upload_to="book/", null=True, verbose_name=u"책 이미지")
    summary = models.TextField(null=True, blank=True, verbose_name=u"책 설명")
    ccl_left = models.CharField(max_length=20, null=True, choices=CCL_LEFT, verbose_name=u"저작물의 영리목적 이용을 허락합니까?")
    ccl_right = models.CharField(max_length=20, null=True, choices=CCL_RIGHT, verbose_name=u"저작물의 변경을 허락합니까?")
    adv_yn = models.CharField(max_length=1, default="N", choices=ADV_YN_CHOICES, verbose_name=u"광고를 표시합니까?")
    adv_content = models.TextField(null=True, blank=True, verbose_name=u"광고 내용")

    def __unicode__(self):
        return self.subject

    def ccl(self):
        result = self.ccl_left + self.ccl_right
        if result[-1] == "-": result = result[:-1]
        return result

    def price(self):
        sell = Sell.objects.filter(book=self)
        if sell: return sell[0].price
        return 0

    def get_absolute_url(self):
        return "/book/{0}".format(self.id)

    def get_first_page(self):
        if self.page_set.count() > 0:
            result = self.page_set.filter(open_yn='Y').order_by("seq")
            if result: return result[0]
        return ""

    def is_sell(self):
        return Sell.objects.filter(book=self).count() > 0

    def is_owner(self, user):
        return user in self.user.all()

    def is_creator(self, user):
        return user == self.creator

    def safe_image(self):
        if not self.image: return "no_image.gif"
        else: return self.image

    def get_plain_authors(self):
        result = []
        for user in self.user.all():
            result.append(user.first_name)
        return ", ".join(result)

    def last_modify_time(self):
        result = Page.objects.filter(book=self).aggregate(max=Max('modify_time'))
        return result.get('max', "")

    def recent_page_comments(self, limit=10):
        return PageComment.objects.filter(page__book=self).order_by("-create_time")[:limit]

    def recent_pages(self, limit=10):
        return self.page_set.order_by("-modify_time")[:limit]


def get_upload_path(instance, filename):
    if isinstance(instance, PageImage):
        return os.path.join("page", "%d" % instance.page.id, filename)
    else:
        # return "page/%s/%s" % (instance.id, filename)
        return os.path.join("page", "%d" % instance.id, filename)


class Page(models.Model):
    subject = models.CharField(max_length=100, verbose_name=u"제목")
    content = models.TextField(verbose_name=u"내용")
    book = models.ForeignKey(Book, verbose_name=u"책선택")
    parent = models.ForeignKey('self', null=True, blank=True, verbose_name=u"부모페이지")
    create_time = models.DateTimeField(default=datetime.datetime.today)
    modify_time = models.DateTimeField(default=datetime.datetime.today)
    viewer = models.ManyToManyField(Ip, null=True, related_name="page_viewer")
    open_yn = models.CharField(max_length=1, default="Y", choices=OPEN_YN_CHOICES, verbose_name=u"공개/비공개")
    seq = models.IntegerField(default=0)
    depth = models.IntegerField(default=0)
    image = models.ImageField(upload_to=get_upload_path, null=True, blank=True, verbose_name=u"이미지삽입")

    def __unicode__(self):
        return self.subject


    def subject_margin(self):
        return self.depth * 20

    def depth_subject(self):
        return format_html(u'<span style="padding-left: {0}px;">{1}</span>',
                           self.subject_margin(),
                           self.subject)

    def get_absolute_url(self):
        return "/{0}".format(self.id)

    def _make_parents(self, page, pages=None):
        if page.parent:
            pages.insert(0, page.parent)
            self._make_parents(page.parent, pages)

    def get_parents(self):
        result = []
        self._make_parents(self, result)
        return result

    def prev(self):
        try:
            return Page.objects.filter(book=self.book, seq__lte=self.seq-1, open_yn="Y").order_by("-seq")[0]
        except:
            return ""

    def next(self):
        try:
            return Page.objects.filter(book=self.book, seq__gte=self.seq+1, open_yn="Y").order_by("seq")[0]
        except:
            return ""

    def is_closed_for_buy(self):
        return self.open_yn == "N" and self.book.is_sell()


class PageImage(models.Model):
    page = models.ForeignKey(Page)
    image = models.ImageField(upload_to=get_upload_path, null=True, blank=True, verbose_name=u"이미지")


class Sell(models.Model):
    book = models.ForeignKey(Book)
    price = models.IntegerField()
    filename =  models.CharField(max_length=100, verbose_name=u"파일명")

    def __unicode__(self):
        return self.book.subject


SEND_YN_CHOICES = (
    ("Y", u"발송완료"),
    ("N", u"미발송"),
)

MONEY_YN_CHOICES = (
    ("Y", u"입금완료"),
    ("N", u"미입금"),
)
class Buy(models.Model):
    book = models.ForeignKey(Book)
    buyer = models.CharField(max_length=100, verbose_name=u"구매자")
    email = models.CharField(max_length=200, verbose_name=u"이메일")
    telno = models.CharField(max_length=20, verbose_name=u"전화번호")
    create_time = models.DateTimeField(default=datetime.datetime.today, verbose_name=u"구매일시")
    send_yn = models.CharField(max_length=1, default="N", choices=SEND_YN_CHOICES, verbose_name=u"발송여부")
    money_yn = models.CharField(max_length=1, default="N", choices=MONEY_YN_CHOICES, verbose_name=u"입금여부")

    def __unicode__(self):
        return u"%s(%s) - %s (%s원)" % (self.buyer, self.email, self.telno, self.book.price())


class BookComment(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name=u"작성자", null=True, blank=True)
    book = models.ForeignKey(Book)
    content = models.TextField(verbose_name=u"댓글내용")
    create_time = models.DateTimeField(default=datetime.datetime.today)


class PageComment(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name=u"작성자", null=True, blank=True)
    page = models.ForeignKey(Page)
    content = models.TextField(verbose_name=u"댓글내용")
    create_time = models.DateTimeField(default=datetime.datetime.today)


@receiver(post_delete, sender=PageImage)
def photo_post_delete_handler(sender, **kwargs):
    pageImage = kwargs['instance']
    storage, path = pageImage.image.storage, pageImage.image.path
    storage.delete(path)
