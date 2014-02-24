# -*- coding: utf-8 -*-
from datetime import datetime
from django.contrib import admin
from django import forms
from django.db import models
from django.forms.util import flatatt
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from reversion_compare.admin import CompareVersionAdmin
from book.cache import cache_clear
from book.models import Book, Ip, Page, Sell, Buy, BookComment, PageComment
from utils import getTree
from tasks import make_and_send
from daterange_filter.filter import DateRangeFilter

class MarkDownEditorWidget(forms.Textarea):
    def render(self, name, value, attrs=None):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        return mark_safe(u"""
<div class="markdown_editor">
    <div class="toolbar">
        <span class="button-h1" accesskey="1" title="Heading 1"><img src="/static/markdown/images/h1.png" /></span>
        <span class="button-h2" accesskey="2" title="Heading 2"><img src="/static/markdown/images/h2.png" /></span>
        <span class="button-h3" accesskey="3" title="Heading 3"><img src="/static/markdown/images/h3.png" /></span>
        <span class="button-bold" accesskey="b" title="Bold text"><img src="/static/markdown/images/bold.png" /></span>
        <span class="button-italic" accesskey="i" title="Italic text"><img src="/static/markdown/images/italic.png" /></span>
        <span class="divider">&nbsp;</span>
        <span class="button-bullets" accesskey="l" title="Bullet List"><img src="/static/markdown/images/bullets.png" /></span>
        <span class="button-numbers" accesskey="n" title="Ordered list"><img src="/static/markdown/images/numbers.png" /></span>
        <span class="divider">&nbsp;</span>
        <span class="button-sourcecode" accesskey="k" title="Source code"><img src="/static/markdown/images/source_code.png" /></span>
        <span class="button-quote" accesskey="q" title="Quotation"><img src="/static/markdown/images/document_quote.png" /></span>
        <span class="divider">&nbsp;</span>
        <span class="button-link" accesskey="l" title="Insert link"><img src="/static/markdown/images/link.png" /></span>
        <span class="button-image" accesskey="p" title="Insert picture/image"><img src="/static/markdown/images/picture.png" /></span>
    </div>
    <textarea%s>%s</textarea>
</div>""" % (flatatt(final_attrs),
                conditional_escape(force_unicode(value))))


class BookAdmin(CompareVersionAdmin):
    history_latest_first = True
    ignore_duplicate_revisions = True

    list_display =  ('subject', 'open_yn', 'create_time')
    fields = ('subject', 'open_yn', 'image', 'creator', 'user', 'summary', 'ccl_left', 'ccl_right')

    formfield_overrides = {
        models.TextField: {'widget': MarkDownEditorWidget},
    }

    class Media:
        css = {
            "all": (
                "/static/myadmin/css/admin.css",
            )
        }
        js = (
            "https://code.jquery.com/jquery-1.8.3.js",
            "/static/markdown/jquery.markdown-0.2.js",
            "/static/markdown/textselector.js",
            "/static/markdown/jquery.griffin.editor.js",
            "/static/markdown/jquery.griffin.editor.markdown.js",
            "/static/myadmin/js/admin.js",
        )

    def save_model(self, request, obj, form, change):
        obj.modify_time = datetime.now()
        # obj.creator = request.user
        obj.save()
        obj.user.add(request.user)

    def queryset(self, request):
        qs = super(BookAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def get_form(self, request, obj=None, **kwargs):
        current_user = request.user
        if not current_user.is_superuser:
            self.fields = ('subject', 'open_yn', 'image', 'summary', 'ccl_left', 'ccl_right')
            #self.exclude = ('user',)
        form = super(BookAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = current_user
        return form


class PageListFilter(admin.SimpleListFilter):
    title = _(u'책 제목')
    parameter_name = 'book_id'

    def lookups(self, request, model_admin):
        if not request.user.is_superuser:
            books = Book.objects.filter(user=request.user)
        else:
            books = Book.objects.all()
        result = []
        for book in books:
            result.append((book.id, _(book.subject)))
        return tuple(result)

    def queryset(self, request, queryset):
        if not request.user.is_superuser:
            queryset = queryset.filter(book__user=request.user)
        if self.value():
            queryset = queryset.filter(book__id=self.value())
        return queryset


class PageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        try:
            self.fields['parent'].queryset = Page.objects.filter(book=self.instance.book)
        except:
            pass


class PageAdmin(CompareVersionAdmin):
    history_latest_first = True
    ignore_duplicate_revisions = True

    form = PageForm
    exclude = ('viewer', 'create_time', 'seq', 'depth', 'modify_time')
    search_fields = ['subject', 'content']
    list_display =  ('depth_subject', 'open_yn', 'modify_time')
    list_filter = (PageListFilter,)
    ordering = ('seq',)

    formfield_overrides = {
        models.TextField: {'widget': MarkDownEditorWidget},
    }

    class Media:
        css = {
            "all": (
                "/static/myadmin/css/admin.css",
            )
        }
        js = (
            "https://code.jquery.com/jquery-1.8.3.js",
            "/static/markdown/jquery.markdown-0.2.js",
            "/static/markdown/textselector.js",
            "/static/markdown/jquery.griffin.editor.js",
            "/static/markdown/jquery.griffin.editor.markdown.js",
            "/static/myadmin/js/admin.js",
        )

    def queryset(self, request):
        qs = super(PageAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(book__user=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "book" and not request.user.is_superuser:
            kwargs["queryset"] = Book.objects.filter(user=request.user)
        if db_field.name == "parent" and not request.user.is_superuser:
            kwargs["queryset"] = Page.objects.filter(book__user=request.user).order_by("seq")
        return super(PageAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.modify_time = datetime.now()
        obj.save()
        self.rearrange_page(obj.book)
        cache_clear(obj.book)

    def rearrange_page(self, book):
        pages = Page.objects.filter(book=book).order_by("-subject")
        for page in getTree(pages):
            if page.seq_changed:
                page.save()


class BuyAdmin(admin.ModelAdmin):
    list_display =  ('book', 'buyer', 'email', 'telno', 'create_time', 'money_yn', 'send_yn')
    readonly_fields = Buy._meta.get_all_field_names()
    search_fields = ['buyer', 'email', 'telno', 'book__subject']
    list_filter = (
        "send_yn",
        "money_yn",
        ("create_time", DateRangeFilter),
    )

    def has_add_permission(self, request, obj=None):
        if request.user.is_superuser: return True
        else: return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser: return True
        else: return False
    # def has_change_permission(self, request, obj=None):
    #     return False

    def queryset(self, request):
        qs = super(BuyAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(book__user=request.user)

    def get_form(self, request, obj=None, **kwargs):
        if obj:     # we are in edit mode
            if request.user.is_superuser:
                self.readonly_fields = ()
            else:
                if "send_yn" in self.readonly_fields:
                    self.readonly_fields.remove("send_yn")
        return super(BuyAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.save()
        if obj.money_yn == "Y" and obj.send_yn == "N":
            make_and_send.delay(obj)


class BookCommentAdmin(admin.ModelAdmin):
    list_display =  ('user', 'name', 'book', 'create_time', 'create_time', 'content')


class PageCommentAdmin(admin.ModelAdmin):
    list_display =  ('user', 'name', 'page', 'create_time', 'create_time', 'content')


admin.site.register(Book, BookAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Ip)
admin.site.register(Sell)
admin.site.register(Buy, BuyAdmin)
admin.site.register(BookComment, BookCommentAdmin)
admin.site.register(PageComment, PageCommentAdmin)
