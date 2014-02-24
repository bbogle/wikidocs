# -*- coding: utf-8 -*-
from django import forms

class BookEditForm(forms.Form):
    subject = forms.CharField(max_length=100, required=True, label=u"책 제목")


class PageEditForm(forms.Form):
    subject = forms.CharField(max_length=100, required=True, label=u"페이지 제목")
    content = forms.CharField(required=True, label=u"페이지 내용")


class BuyForm(forms.Form):
    buyer = forms.CharField(max_length=100, required=True, label=u"신청자 이름")
    email = forms.EmailField(max_length=100, required=True, label=u"이메일")
    telno = forms.RegexField(max_length=15, regex=r"\d{2,3}[-]\d{3,4}[-]\d{4}", required=True, label=u"전화번호")
    agree = forms.BooleanField(required=True, label=u"환불규정")