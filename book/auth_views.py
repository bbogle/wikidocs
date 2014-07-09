# -*- coding: utf-8 -*-
## login, logout ##
import traceback
from django.contrib import auth
from django.contrib.auth.models import User, Group
from django.core.context_processors import csrf
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template import Context
from django.template.loader import get_template

import random
import base64
from book.auth_forms import JoinForm, PasswordForm


def loginForm(request, errorMsg=None):
    email = request.POST.get('email', "")
    next = request.GET.get('next', "/")

    if not email:
        email = request.COOKIES.get('email', "")

    passwd = request.COOKIES.get('passwd', "")
    c = {
        "errorMsg": errorMsg,
        "email": email,
        "passwd": passwd,
        "next": next,
    }
    c.update(csrf(request))

    html = get_template('auth/login.html').render(
        Context(c)
    )
    response = HttpResponse(html)
    return response


def login(request):
    email = request.POST.get('email', "")
    passwd = request.POST.get('passwd', "")
    passwd_remember = request.POST.get("passwd_remember", "")
    next = request.POST.get("next", "/")
    user = auth.authenticate(username=email, password=passwd)

    if user is not None:
        if user.is_active:
            auth.login(request, user)

            # save cookie
            response = HttpResponseRedirect(next)
            week = 60 * 60 * 24 * 7
            response.set_cookie('email', email, max_age=week)
            if passwd_remember:
                response.set_cookie('passwd', passwd, max_age=week)
            else:
                response.delete_cookie('passwd')

            return response

        else:
            return loginForm(request, errorMsg=u"사용이 정지된 계정입니다.")
    else:
        return loginForm(request, errorMsg=u"이메일/비밀번호를 확인하세요.")


def joinForm(request, errorMsg=None):
    error = request.session.get("error")
    c = {
        "errorMsg": errorMsg,
        "email":request.POST.get('email', ""),
        "error": error,
    }
    c.update(csrf(request))

    html = get_template('auth/join.html').render(
        Context(c)
    )
    response = HttpResponse(html)
    if error: del request.session["error"]
    return response


def join(request):
    form = JoinForm(request.POST)
    if not form.is_valid():
        request.session["error"] = form
        return redirect("/joinForm")

    email = request.POST.get('email', "")
    username = request.POST.get('username', "")
    passwd = request.POST.get('passwd', "")

    try:
        if User.objects.filter(username=email).count() == 0:
            user = User.objects.create_user(email, email, passwd)
            user.first_name = username
            user.is_staff = True
            user.save()

            g = Group.objects.get(name='wikidocs')
            g.user_set.add(user)

            user = auth.authenticate(username=email, password=passwd)
            auth.login(request, user)
            return HttpResponseRedirect("/")
        else:
            request.session["error"] = form
            return joinForm(request, errorMsg=u"이미 사용중인 이메일입니다: [%s]" % email)
    except:
        request.session["error"] = form
        return joinForm(request, errorMsg=u"가입에 일시적인 장애가 있습니다..")


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")


def passwdForm(request, errorMsg=None, successMsg=None):
    error = request.session.get("error")
    c = {
        "errorMsg": errorMsg,
        "successMsg": successMsg,
        "email":request.POST.get('email', ""),
        "error": error,
    }
    c.update(csrf(request))

    html = get_template('auth/passwd.html').render(
        Context(c)
    )
    response = HttpResponse(html)
    if error: del request.session["error"]
    return response


def randomString(leng):
    nbits = leng * 6 + 1
    bits = random.getrandbits(nbits)
    uc = u"%0x" % bits
    newlen = int(len(uc) / 2) * 2 # we have to make the string an even length
    ba = bytearray.fromhex(uc[:newlen])
    return base64.urlsafe_b64encode(str(ba))[:leng].lower()


def passwd_send(request):
    form = PasswordForm(request.POST)
    if not form.is_valid():
        request.session["error"] = form
        return redirect("/passwdForm")

    email = request.POST.get('email', "")
    try:
        from sendmail import sendEmail
        passwd = randomString(4)

        email_msg = u"위키독스 비밀번호가 초기화 되었습니다. 새 비밀번호:%s" % passwd
        sendEmail(email, u"위키독스 비빌번호 변경 알림", email_msg)

        u = User.objects.get(username=email)
        u.set_password(passwd)
        u.save()

        return passwdForm(request, successMsg=u"이메일로 재 성성된 비밀번호를 발송했습니다.")
    except:
        print traceback.format_exc()
        return passwdForm(request, errorMsg=u"이메일 송신이 실패했습니다.")


def social_auth(request):
    if not request.user.email: return social_auth_error(request)
    changed = False
    user = request.user

    users = User.objects.filter(username=user.email)
    if not users: # first user
        user.username = user.email
        if not user.first_name:
            user.first_name = user.email.split("@")[0]
        user.is_staff = True
        user.save()

        g = Group.objects.get(name='wikidocs')
        g.user_set.add(user)

    user = User.objects.get(username=user.email)
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    auth.login(request, user)
    return HttpResponseRedirect("/")


def social_auth_error(request):
    request.session["error_message"] = u"Social 로그인에 실패했습니다."
    return HttpResponseRedirect("/")