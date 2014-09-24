# -*- coding: utf-8 -*-
import datetime
import json
from django.template import RequestContext

try: from PIL import Image
except:import Image

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.core.files.base import ContentFile
from django.db.models import Count, Q
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
import reversion
from book.cache import cache_get, cache_put, cache_clear, cache_remove
from book.forms import PageEditForm, BookEditForm, BuyForm
from book.models import Book, Page, Sell, Buy, Ip, BookComment, PageComment, PageImage

from book.utils import getTree

if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
    from django.core.mail import send_mail


# ----------
# utility functions
def my_render(request, tmpl, args):
    return render(request, tmpl, args, context_instance=RequestContext(request))


def update_context(request, ctx):
    result = False
    session_keys = ["ok_message", "error_message"]
    for session_key in session_keys:
        if request.session.has_key(session_key):
            session_value = request.session.get(session_key, "")
            del request.session[session_key]
            ctx.update({
                session_key:session_value
            })
            result = True
    ctx.update(csrf(request))
    return result


# ----------
# index

def index(request):
    tab_name = request.session.get("tab", "sell")
    result = index_tab(request, tab_name)

    context = {"tab":result.content, "tab_name":tab_name}
    update_context(request, context)
    return my_render(request, 'book/index.html', context)

    # return render(request, 'book/index.html', {"tab":result.content, "tab_name":tab_name})


def index_tab(request, name):
    if name == "sell":
        books = []
        for sell in Sell.objects.annotate(
                num_recommend=Count('book__recommend')).filter(book__open_yn='Y').order_by("-num_recommend"):
            books.append(sell.book)

    elif name == "share":

        # open_yn = 'Y'
        # recommend >= 5
        # page count >= 5

        books = filter(lambda x: x.page_set.count()>=5,
                       Book.objects.annotate(num_recommends=Count('recommend')).filter(
                            open_yn='Y', num_recommends__gte=5).order_by("-num_recommends"))

    elif name == "mybook":
        books = Book.objects.filter(user=request.user)
        books = sorted(books, key=lambda a: a.last_modify_time(), reverse=True)

    request.session['tab'] = name
    context = {"books": books, "tab_name":name}
    return render(request, 'book/index_tab.html', context)


@csrf_protect
def buy(request, _id):
    error = request.session.get("error")

    book = Book.objects.get(id=_id)
    context ={"book": book, "error": error}
    context.update(csrf(request))

    if not book.is_sell() or book.price() == 0:
        return redirect("/book/%s" % book.id)

    if error: del request.session["error"]
    return render(request, 'book/buy.html', context)


@csrf_protect
def buy_save(request):
    book_id = request.POST.get("book_id")
    book = Book.objects.get(id=book_id)

    if not book.is_sell() or book.price() == 0:
        return redirect("/book/%s" % book.id)

    form = BuyForm(request.POST)
    if not form.is_valid():
        request.session["error"] = form
        return redirect("/buy/%s" % book_id)

    buyer = request.POST.get("buyer")
    email = request.POST.get("email")
    telno = request.POST.get("telno")

    buy = Buy(book=book, buyer=buyer, email=email, telno=telno)
    buy.save()

    context ={"buy": buy, "book": buy.book}
    info = render(request, 'book/buy_info.html', context)
    mail_body = info.content

    # send to buyer
    send_mail(u"%s 님, %s 구매신청이 완료되었습니다" % (buyer, book.subject),
              mail_body,
              settings.DEFAULT_FROM_EMAIL,
              [buy.email, settings.ADMINS[0][1]])

    # # send to admin
    # send_mail(u"책 구매 발생: %s" % buy.buyer,
    #           str(book)+":"+str(buy),
    #           settings.DEFAULT_FROM_EMAIL,
    #           [settings.ADMINS[0][1]])

    return render(request, 'book/buy_save.html', context)


# ----------
# book
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_ip(request):
    client_ip = get_client_ip(request)
    try:
        ip = Ip.objects.get(ip=client_ip)
    except Ip.DoesNotExist:
        try:
            ip = Ip(ip=client_ip)
            ip.save()
        except:pass
    return ip


def check_auth(request, book, page=None):
    if (page and page.open_yn == "N") or book.open_yn == "N":
        if not request.user.is_authenticated():
            raise Http404
        elif request.user not in book.user.all():
            raise Http404


def getToc(request, book):
    isAuthor = request.user in book.user.all()
    if isAuthor:
        toc = Page.objects.filter(book=book).order_by("seq")
    else:
        toc = Page.objects.filter(book=book, open_yn="Y").order_by("seq")
    return toc


def book(request, _id):
    cache = cache_get(request, "book_%s" % _id)
    if cache: return HttpResponse(cache)

    try:
        book = Book.objects.get(id=_id)
    except Book.DoesNotExist:
        return redirect("/")

    toc = getToc(request, book)

    check_auth(request, book)
    context = {"book": book, "toc":toc}
    update_context(request, context)
    result = my_render(request, 'book/book.html', context)
    cache_put(request, "book_%s" % _id, result.content)
    return result


def book_recommend(request, _id):
    book = Book.objects.get(id=_id)
    ip = get_ip(request)
    if ip not in book.recommend.all():
        book.recommend.add(ip)
        cache_remove("book_%s" % book.id)
    return redirect("/book/%s" % book.id)


@login_required
def book_comment_save(request):
    book_id = request.POST.get("book_id")
    content = request.POST.get("content")

    book = Book.objects.get(id=book_id)
    bc = BookComment(user=request.user, book=book, content=content)
    bc.save()
    cache_remove("book_%s" % book.id)

    body = u"""%(user)s 님의 댓글 (작성일시: %(create_time)s)
-----------------------------------------------------------------------------

%(content)s

-----------------------------------------------------------------------------
%(subject)s URL : http://wikidocs.net/book/%(book_id)s
    """ % {
        "user": request.user.first_name,
        "create_time": bc.create_time.strftime(u"%Y-%m-%d %X"),
        "content": content,
        "book_id": book.id,
        "subject": book.subject
    }

    emails = []
    for user in book.user.all():
        if user != request.user:
            emails.append(user.email)

    # 댓글에 이름 언급 시 이메일 송신
    for bc in BookComment.objects.filter(book=book):
        if content.find(bc.user.first_name) != -1 and bc.user != request.user and bc.user.email not in emails:
            emails.append(bc.user.email)

    send_mail(u"%s 에 댓글이 작성되었습니다." % (book.subject),
              body,
              settings.DEFAULT_FROM_EMAIL,
              emails)

    result = render(request, 'book/include/book_comment.html', {"book": book})
    return HttpResponse(result.content)


@login_required
def book_comment_remove(request):
    comment_id = request.POST.get("comment_id")
    comment = BookComment.objects.get(id=comment_id)
    book = comment.book
    if request.user == comment.user:
        comment.delete()
    result = render(request, 'book/include/book_comment.html', {"book": book})
    return HttpResponse(result.content)


# ----------
# page

def page(request, _id):
    cache = cache_get(request, _id)
    if cache: return HttpResponse(cache)

    try:
        page = Page.objects.get(id=_id)
    except Page.DoesNotExist:
        return redirect("/")

    if page.is_closed_for_buy() and not page.book.is_owner(request.user):
        return redirect("/buy/%s" % page.book.id)

    check_auth(request, page.book, page)
    toc = getToc(request, page.book)
    context = {"page": page, "book": page.book, "toc": toc}
    update_context(request, context)
    result = my_render(request, 'book/page.html', context)
    cache_put(request, _id, result.content)
    return result


@login_required
def page_comment_save(request):
    page_id = request.POST.get("page_id")
    content = request.POST.get("content")

    page = Page.objects.get(id=page_id)
    pc = PageComment(user=request.user, page=page, content=content)
    pc.save()

    cache_remove("book_%s" % page.book.id)
    cache_remove(page.id)

    body = u"""%(user)s 님의 댓글 (작성일시: %(create_time)s)
-----------------------------------------------------------------------------

%(content)s

-----------------------------------------------------------------------------
%(subject)s URL : http://wikidocs.net/%(page_id)s
    """ % {
        "user": request.user.first_name,
        "create_time": pc.create_time.strftime(u"%Y-%m-%d %X"),
        "content": content,
        "page_id": page.id,
        "subject": page.subject
    }

    emails = []
    for user in page.book.user.all():
        if user != request.user:
            emails.append(user.email)

    # 댓글에 이름 언급 시 이메일 송신
    for pc in PageComment.objects.filter(page=page):
        if pc.user and content.find(pc.user.first_name) != -1 \
                and pc.user != request.user and pc.user.email not in emails:
            emails.append(pc.user.email)

    send_mail(u"%s 페이지에 댓글이 작성되었습니다." % (page.subject),
              body,
              settings.DEFAULT_FROM_EMAIL,
              emails)

    result = render(request, 'book/include/page_comment.html', {"page": page})
    return HttpResponse(result.content)


@login_required
def page_comment_remove(request):
    comment_id = request.POST.get("comment_id")
    comment = PageComment.objects.get(id=comment_id)
    page = comment.page
    if request.user == comment.user:
        comment.delete()
        cache_remove("book_%s" % page.book.id)
        cache_remove(page.id)

    result = render(request, 'book/include/page_comment.html', {"page": page})
    return HttpResponse(result.content)



@login_required
def page_comment_edit(request, c_id):
    if request.method == "GET":
        comment = PageComment.objects.get(id=c_id)

        if request.user != comment.user and not request.user.is_staff:
            comment.page.id
            request.session["error_message"] = u"댓글을 수정할 수 있는 권한이 없습니다"
            return redirect('/%s' % comment.page.id)

        c = {"comment": comment}
        update_context(request, c)
        return my_render(request, 'book/include/page_comment_edit.html', c)

    elif request.method == "POST":

        comment = PageComment.objects.get(id=c_id)
        content = unicode.strip(request.POST.get("content", ""))
        comment.content = content
        comment.save()

        cache_remove("book_%s" % comment.page.book.id)
        cache_remove(comment.page.id)

        request.session["ok_message"] = u"댓글이 수정되었습니다"
        return redirect('/%s#comment_%s' % (comment.page.id, c_id))


# ----------
# edit
@login_required
def edit_book(request, book_id):
    book = Book.objects.get(id=book_id)

    if request.user not in book.user.all():
        request.session["error_message"] = u"수정권한이 없습니다"
        return redirect('/book/%s' % book.id)


    toc = Page.objects.filter(book=book).order_by("seq")

    message = request.session.get("edit_message")
    error = request.session.get("error")
    context = {"toc": toc, "book": book, "message": message, "error": error}

    if message: del request.session["edit_message"]
    if error: del request.session["error"]
    response = render(request, 'book/edit_book.html', context)
    response["X-XSS-Protection"] = "0"
    return response


def edit_book_user(request):
    kw = request.POST.get("kw", "")
    users = None
    if kw:
        users = User.objects.filter(Q(first_name__contains=kw) | Q(email__contains=kw), ~Q(id=request.user.id))
    return render(request, 'book/include/edit_book_user.html', {"users": users})


def edit_book_user_add(request):
    user_id = request.POST.get("user_id")
    book_id = request.POST.get("book_id")

    book = Book.objects.get(id=book_id)
    user = User.objects.get(id=user_id)

    if user not in book.user.all():
        book.user.add(user)

    return render(request, 'book/include/edit_book_author.html', {"book": book})


def edit_book_user_del(request):
    user_id = request.POST.get("user_id")
    book_id = request.POST.get("book_id")

    book = Book.objects.get(id=book_id)
    user = User.objects.get(id=user_id)

    users = book.user.all()
    if len(users)>1 and user in users and not book.is_creator(user):
        book.user.remove(user)

    return render(request, 'book/include/edit_book_author.html', {"book": book})


@login_required
def edit_page(request, page_id):
    page = Page.objects.get(id=page_id)

    if request.user not in page.book.user.all():
        request.session["error_message"] = u"수정권한이 없습니다"
        return redirect('/%s' % page.id)

    toc = Page.objects.filter(book=page.book).order_by("seq")

    message = request.session.get("edit_message")
    error = request.session.get("error")
    context = {"toc": toc, "page": page, "book": page.book,
               "message": message, "error": error,
               "range50":range(0, 1000, 50)}

    if message: del request.session["edit_message"]
    if error: del request.session["error"]
    response = render(request, 'book/edit_page.html', context)
    response["X-XSS-Protection"] = "0"
    return response


def rearrange_page(book):
    pages = Page.objects.filter(book=book).order_by("-subject")
    for page in getTree(pages):
        if page.seq_changed or page.__dict__.has_key('depth_changed'):
            page.save()


def edit_book_save(request):
    action = request.POST.get("action")
    book_id = request.POST.get("book_id")
    subject = request.POST.get("subject")
    summary = request.POST.get("content")
    open_yn = request.POST.get("open_yn")
    ccl_left = request.POST.get("ccl_left")
    ccl_right = request.POST.get("ccl_right")
    adv_yn = request.POST.get("adv_yn")
    adv_content = request.POST.get("adv_content")
    adv_mobile_content = request.POST.get("adv_mobile_content")

    book = Book.objects.get(id=book_id)

    if request.user not in book.user.all():
        request.session["error_message"] = u"수정권한이 없습니다"
        return redirect('/book/%s' % book.id)

    if action == "modify":
        form = BookEditForm(request.POST)
        if not form.is_valid():
            request.session["error"] = form
        else:
            reversion_comments = []
            if book.subject != subject: reversion_comments.append(u"제목")
            if book.summary != summary: reversion_comments.append(u"책요약")
            if book.open_yn != open_yn: reversion_comments.append(u"공개여부")
            if book.ccl_left != ccl_left or book.ccl_right != ccl_right: reversion_comments.append(u"저작권")

            book.subject = subject
            book.summary = summary
            book.open_yn = open_yn
            book.ccl_left = ccl_left
            book.ccl_right = ccl_right
            book.adv_yn = adv_yn
            book.adv_content = adv_content
            book.adv_mobile_content = adv_mobile_content
            book.modify_time = datetime.datetime.now()

            if 'image' in request.FILES:
                file_content = ContentFile(request.FILES['image'].read())
                book.image.save(request.FILES['image'].name, file_content)
                reversion_comments.append(u"이미지")
                resize_image(book.image.path, width=100, height=130)

            if reversion_comments:
                reversion.set_comment(u"%s (이)가 변경되었습니다." % u", ".join(reversion_comments))

            book.save()
            request.session["edit_message"] = u"책이 수정되었습니다"

    elif action == "add":
        book = Book(subject=subject, summary=summary, open_yn=open_yn, ccl_left=ccl_left, ccl_right=ccl_right, creator=request.user)
        book.save()
        book.user.add(request.user)

        page = Page(book=book, subject="FrontPage")
        page.save()

        if 'image' in request.FILES:
            file_content = ContentFile(request.FILES['image'].read())
            book.image.save(request.FILES['image'].name, file_content)

        request.session["edit_message"] = u"책이 추가되었습니다"

    elif action == "delete":
        book.delete()
        # request.session["edit_book_message"] = u"책이 삭제되었습니다"

    # rearrange_page(page.book)
    cache_clear(book)

    if action == "delete":
        return redirect("/")
    else:
        return redirect("/edit/book/%s" % book.id)


def edit_book_new(request):
    book = Book(subject="New Book", ccl_left="by", ccl_right="-", summary="", open_yn = "N", creator=request.user)
    book.save()
    book.user.add(request.user)

    page = Page(book=book, subject="FrontPage")
    page.save()

    return redirect("/edit/book/%s" % book.id)


def edit_page_new(request, book_id):
    book = Book.objects.get(id=book_id)
    page = Page(book=book, subject="New Page")
    page.save()
    cache_clear(book)
    rearrange_page(book)
    return redirect("/edit/page/%s" % page.id)


def edit_page_save(request):
    action = request.POST.get("action")
    page_id = request.POST.get("page_id")
    subject = request.POST.get("subject")
    content = request.POST.get("content")
    open_yn = request.POST.get("open_yn")
    parent_id = request.POST.get("parent")
    if parent_id: parent = Page.objects.get(id=parent_id)
    else:parent = None

    page = Page.objects.get(id=page_id)
    if request.user not in page.book.user.all():
        request.session["error_message"] = u"수정권한이 없습니다"
        return redirect('/%s' % page.id)

    if action == "modify":
        form = PageEditForm(request.POST)
        if not form.is_valid():
            request.session["error"] = form
            ret_json = { 'success': False}
            return HttpResponse(json.dumps(ret_json ))

        else:
            # json response

            reversion_comments = []
            if page.subject != subject: reversion_comments.append(u"제목")
            if page.content != content: reversion_comments.append(u"내용")
            if page.parent != parent: reversion_comments.append(u"부모페이지")
            if page.open_yn != open_yn: reversion_comments.append(u"공개여부")

            def is_toc_changed():
                return page.parent != parent \
                        or page.open_yn != open_yn \
                        or page.subject != subject

            toc_changed = is_toc_changed()

            page.subject = subject
            page.content = content
            page.parent = parent
            page.open_yn = open_yn
            page.modify_time = datetime.datetime.now()
            page.save()

            if reversion_comments:
                reversion.set_comment(u"%s (이)가 변경되었습니다." % u", ".join(reversion_comments))

            ret_json = { 'success': not toc_changed, 'msg': u"페이지가 수정되었습니다"}

            cache_clear(page.book)
            rearrange_page(page.book)

            return HttpResponse(json.dumps( ret_json ))

    elif action == "add":
        page = Page(book=page.book, subject=subject, parent=parent, content=content, open_yn=open_yn)
        page.save()
        request.session["edit_message"] = u"페이지가 추가되었습니다"

    elif action == "delete":
        page.delete()
        request.session["edit_message"] = u"페이지가 삭제되었습니다"

    # page.book.modify_time = datetime.datetime.now()
    # page.book.save()

    cache_clear(page.book)
    rearrange_page(page.book)

    if action == "delete":
        return redirect("/edit/book/%s" % page.book.id)
    else:
        return redirect("/edit/page/%s" % page.id)

def resize_image(imageFile, width=0, height=0):
    max_width = int(width) * 1.0
    max_height = int(height) * 1.0
    im = Image.open(imageFile)
    org_size = im.size

    # print "max_width:%s, max_height:%s" % (max_width, max_height)

    if max_width == 0: return
    if max_height == 0 and org_size[0] <= max_width:
        return
    if max_height == 0 and org_size[0] > max_width:
        ratio = max_width/org_size[0]
        new_size = (int(org_size[0]*ratio), int(org_size[1]*ratio))
        im.thumbnail(new_size, Image.ANTIALIAS)
        im = im.convert('RGB')
        im.save(imageFile)

    elif org_size[0] > max_width or org_size[1] > max_height:
        ratio = min(max_width/org_size[0], max_height/org_size[1])
        new_size = (int(org_size[0]*ratio), int(org_size[1]*ratio))
        im.thumbnail(new_size, Image.ANTIALIAS)
        im = im.convert('RGB')
        im.save(imageFile)


def edit_page_image_upload(request):
    # if request.method == "POST":
    upload = request
    is_raw = True
    try:
        filename = request.GET[ 'qqfile' ]
    except KeyError:
        return HttpResponseBadRequest( "AJAX request not valid" )

    page_id = request.GET["page_id"]
    image_size = request.GET["image_size"]
    page = Page.objects.get(id=page_id)

    file_read = []
    foo = upload.read( 1024 )
    file_read.append(foo)
    while foo:
        foo = upload.read(1024)
        file_read.append(foo)

    pageImage = PageImage(page=page)
    pageImage.image.save(filename, ContentFile(''.join(file_read)))
    pageImage.save()

    resize_image(pageImage.image.path, width=image_size)

    result = render(request, 'book/include/edit_page_image.html', {"page": page})
    html = result.content
    ret_json = { 'success': True, 'html': html}
    return HttpResponse(json.dumps( ret_json ))


def edit_page_image_del(request):
    page_image_id = request.POST.get("page_image_id")
    pageImage = PageImage.objects.get(id=page_image_id)
    page = pageImage.page
    pageImage.delete()
    return render(request, 'book/include/edit_page_image.html', {"page": page})


def edit_preview(request):
    preview_content = request.POST.get("preview_content")
    return render(request, 'book/include/edit_preview.html', {"preview_content": preview_content})


# ----------
# help

def help(request, name):
    if name == "wikidocs":
        book = Book.objects.get(subject=u"위키독스", user__email="pahkey@gmail.com")
        return redirect("/book/%s" % book.id)
    else:
        return render(request, 'help/%s.html' % name, {})



# ----------
# feedback

def feedback(request):
    page_id = request.POST.get("page_id")
    print "page_id:%s" % page_id
    email = request.POST.get("email")
    page = Page.objects.get(id=page_id)

    content = u"""%(email)s 님이 전송한 피드백입니다.

----------------------------------------------------------------
책제목 : %(book_subject)s
페이지 : %(page_subject)s

%(feedback)s
----------------------------------------------------------------

※ 이 메일은 발신전용 메일입니다. 답장은 %(email)s 님에게 남겨주세요.
    """ % {"feedback": request.POST.get("feedback"),
           "email": email,
           "book_subject": page.book.subject,
           "page_subject": page.subject,
    }

    author_emails = []
    for user in page.book.user.all():
        author_emails.append(user.email)

    # send to buyer
    send_mail(u"위키독스 피드백이 도착했습니다 : [%s]" % page.subject,
              content,
              settings.DEFAULT_FROM_EMAIL,
              author_emails
    )
    return HttpResponse("ok")


# ----------
# error

def page_404(request):
    return redirect("/")


def page_500(request):
    return render(request, 'error/500.html', {})
