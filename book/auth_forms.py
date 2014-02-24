# -*- coding: utf-8 -*-
from django import forms

class JoinForm(forms.Form):
    email = forms.EmailField(required=True, label=u"이메일")
    username = forms.CharField(max_length=30, required=True, label=u"이름")
    passwd = forms.CharField(widget=forms.PasswordInput, required=True, label=u"비밀번호")


class PasswordForm(forms.Form):
    email = forms.EmailField(required=True, label=u"이메일")
