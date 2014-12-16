# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from book.models import Page, Book, PageComment
from book.views import my_render, update_context

PER_PAGE = 10


@login_required
def edit_base(request):
    user = request.user
    if request.method == "GET":
        c = {}
        update_context(request, c)
        return my_render(request, 'profile/profile_edit_base.html', c)

    elif request.method == "POST":
        _name = request.POST.get("name", "").strip()

        if _name:
            user.first_name = _name
            user.save()
            request.session["ok_message"] = u"기본정보가 수정되었습니다"
        else:
            request.session["error_message"] = u"이름을 입력 해 주세요"

        return redirect('book.profile_views.edit_base')


@login_required
def edit_password(request):
    user = request.user
    if request.method == "GET":
        c = {}
        update_context(request, c)
        return my_render(request, 'profile/profile_edit_password.html', c)
    elif request.method == "POST":
        cpasswd = request.POST["cpasswd"]
        npasswd = request.POST["npasswd"]
        u = User.objects.get(username=user.email)
        if not cpasswd or not npasswd:
            request.session["error_message"] = u"입력값을 확인하세요"

        elif not u.check_password(cpasswd):
            request.session["error_message"] = u"기존 비밀번호가 틀리게 입력되었습니다"
        else:
            u.set_password(npasswd)
            u.save()
            request.session["ok_message"] = u"비밀번호가 변경되었습니다"

        return redirect('book.profile_views.edit_password')


def info(request, u_id):
    try:
        _user = User.objects.get(id=u_id)
    except User.DoesNotExist:
        return redirect("/")

    books = Book.objects.filter(user=_user, open_yn="Y").order_by("-modify_time")
    pages = Page.objects.filter(book__user=_user, book__open_yn="Y", open_yn="Y")\
                .order_by("-modify_time")[:10]
    comments = PageComment.objects.filter(user=_user).order_by("-create_time")
    recommend_count = Book.objects.filter(user=_user).values("recommend").count()

    total_count = comments.count()
    page = int(request.POST.get("page", "1"))
    paginator = Paginator(comments, PER_PAGE)

    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)

    c = {"who":_user,
         "books":books,
         "pages":pages,
         "comments":comments,
         "recommend_count":recommend_count,
         "per_page":PER_PAGE,
         "total_count":total_count,
         }
    update_context(request, c)
    return my_render(request, 'profile/profile_info.html', c)


@login_required
def book(request):
    """
    book list
    """
    books = Book.objects.filter(user=request.user).order_by("-modify_time")

    c = {"books":books,
         }
    update_context(request, c)
    return my_render(request, 'profile/profile_book.html', c)


@login_required
def comment(request):
    """
    comment list
    """
    comments = PageComment.objects.filter(user=request.user).order_by("-create_time")
    total_count = comments.count()
    page = int(request.POST.get("page", "1"))
    paginator = Paginator(comments, PER_PAGE)

    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)

    c = {"comments":comments,
         "per_page":PER_PAGE,
         "total_count":total_count,
         }
    update_context(request, c)
    return my_render(request, 'profile/profile_comment.html', c)