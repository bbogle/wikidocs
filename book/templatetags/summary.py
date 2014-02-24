# -*- coding: utf-8 -*-
from django.template import Library

register = Library()

def summary(src):
    return ' '.join(filter(lambda t:len(t.strip()) < 30, src.split()))

register.filter('summary', summary)