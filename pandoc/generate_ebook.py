# -*- coding: utf-8 -*-
import os
import sys
import re
import urllib
try: from PIL import Image
except:import Image


WIKIDOCS_HOME = "/home/ubuntu/project/wikidocs"
PANDOC_HOME = WIKIDOCS_HOME+"/pandoc"

sys.path.insert(0, WIKIDOCS_HOME)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wikidocs.settings")

from book.models import Book, Page, Buy

from email.mime.text import MIMEText
from email import Encoders, MIMEBase, MIMEMultipart
from email.header import Header

from email.utils import COMMASPACE, formatdate

from django.conf import settings
import smtplib

def utf8(data):
    return unicode(data).encode("utf-8")



def resize_image(imageFile):
    max_width = 300.0
    max_height = 200.0

    im = Image.open(imageFile)
    org_size = im.size
    if org_size[0] > max_width or org_size[1] > max_height:
        ratio = min(max_width/org_size[0], max_height/org_size[1])
        new_size = (int(org_size[0]*ratio), int(org_size[1]*ratio))
        im.thumbnail(new_size, Image.ANTIALIAS)
        im.save(imageFile)


def get_page_image(data, buy_id=None):
    pat = re.compile(r"!\[.*\]\((.*)\)")
    images = pat.findall(data)
    for image in images:
        image_name = os.path.basename(image)
        if buy_id:
            image_file = '%s/md/%s/%s' % (PANDOC_HOME, buy_id, image_name)
        else:
            image_file = '%s/md/%s' % (PANDOC_HOME, image_name)
        f = open(image_file,'wb')
        f.write(urllib.urlopen(image).read())
        f.close()
        resize_image(image_file)
        data = data.replace(image, image_name)
    return data


def mk_tex(water_mark, title, book, buy_id=None):
    f = open("%s/wikidocs-template.tex" % PANDOC_HOME, 'r')
    content = f.read()
    f.close()
    content = content.replace("WATER_MARK", "Licensed to %s" % utf8(water_mark))
    content = content.replace("TITLE", utf8(title))
    content = content.replace("BOOK_SUBJECT", utf8(book.subject))
    content = content.replace("BOOK_AUTHOR", utf8(book.get_plain_authors()))

    if buy_id:
        tex_filename = "%s/md/%s/wikidocs.tex" % (PANDOC_HOME, buy_id)
    else:
        tex_filename = "%s/md/wikidocs.tex" % PANDOC_HOME

    f = open(tex_filename, 'w')
    f.write(content)
    f.close()


def check_book_by_id(book_id):
    book = Book.objects.get(id=book_id)
    pages = Page.objects.filter(book=book, open_yn='Y').order_by("seq")

    for page in pages:
        print page.subject, 'start...'
        f = open("./md/%s.md" % page.id, "w")
        f.write("# %s" % utf8(page.subject))
        content = page.content.replace("\r", "")
        content = content.replace("{.python}", "")
        content = content.replace("{.java}", "")
        content = get_page_image(content)
        f.write("\n\n")
        f.write(utf8(content))
        f.close()

        pandoc_info = {
            "PANDOC_HOME": PANDOC_HOME,
            "MD_ROOT": PANDOC_HOME+"/md",
            "GEN_ROOT": PANDOC_HOME+"/gen",
            "filename": page.id,
        }
        os.system("cd %(MD_ROOT)s;pandoc --latex-engine xelatex --template wikidocs.tex %(filename)s.md -o %(filename)s.pdf" % pandoc_info)


def send_book(buy):
    book = buy.book
    sell = book.sell_set.all()[0]
    admin_email = settings.ADMINS[0][1]
    pandoc_info = {
        "PANDOC_HOME": PANDOC_HOME,
        "MD_ROOT": PANDOC_HOME+"/md",
        "GEN_ROOT": PANDOC_HOME+"/gen",
        "filename": sell.filename,
        "email": buy.email,
        "buy_id": buy.id,
    }

    msg = MIMEMultipart.MIMEMultipart()
    msg['From'] = settings.DEFAULT_FROM_EMAIL
    msg['To'] = COMMASPACE.join([buy.email, admin_email])
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = Header(s=utf8(u"%s 전자책(E-Book)" % book.subject), charset='utf-8')

    text = u""""%(subject)s"을 구매 해 주셔서 감사합니다.

총 3개의 첨부 파일을 확인 해 주시기 바랍니다.

- %(filename)s.pdf (PDF)
- %(filename)s.epub (일반 전자문서)
- %(filename)s.mobi (킨들용 전자문서)

첨부 파일에 문제가 있을 경우 답장주시면 교환 또는 환불 해 드립니다.

문의 : 박응용 (pahkey@gmail.com)

감사합니다.

p.s. 전자문서의 품질이 개선되었을 경우 이메일이 재 발송될 수 있습니다.
""" % {"subject": book.subject, "filename": sell.filename}

    msg.attach(MIMEText(utf8(text), _charset='utf-8'))

    files = []
    files.append("%(GEN_ROOT)s/%(buy_id)s/%(filename)s.pdf" % pandoc_info)
    files.append("%(GEN_ROOT)s/%(buy_id)s/%(filename)s.epub" % pandoc_info)
    files.append("%(GEN_ROOT)s/%(buy_id)s/%(filename)s.mobi" % pandoc_info)

    for f in files:
        part = MIMEBase.MIMEBase('application', "octet-stream")
        part.set_payload( open(f,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        msg.attach(part)

    mailServer = smtplib.SMTP(settings.EMAIL_HOST)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    # msg.set_charset('utf-8')
    mailServer.sendmail(msg["From"], [buy.email, admin_email], msg.as_string())
    mailServer.quit()

    buy.send_yn = "Y"
    buy.save()


def make_ebook(buy):
    book = buy.book
    pages = Page.objects.filter(book=book, open_yn="Y").order_by("seq")

    sell = book.sell_set.all()[0]

    MD_ROOT = PANDOC_HOME+"/md/%s" % buy.id
    if not os.path.exists(MD_ROOT):
        os.makedirs(MD_ROOT)

    pandoc_info = {
        "PANDOC_HOME": PANDOC_HOME,
        "MD_ROOT": MD_ROOT,
        "GEN_ROOT": PANDOC_HOME+"/gen",
        "filename": sell.filename,
        "email": buy.email,
        "book_image_path": book.image.path,
        "buy_id": buy.id,
    }

    os.system("rm -f %(MD_ROOT)s/*" % pandoc_info)
    water_mark = "%s(%s)" % (buy.buyer, buy.email)

    f = open("%(MD_ROOT)s/%(filename)s.md" % pandoc_info, "w")
    result = []
    result.insert(0, u"""# ※ 문서정보

Copyright ⓒ 2013 %(author)s. All rights reserved.%(space)s
이 책의 무단전재와 복제를 금합니다

이 책은 **%(buyer)s** 님이 구매하신 문서입니다.%(space)s
(구매 : [http://wikidocs.net/book/%(book_id)s](http://wikidocs.net/book/%(book_id)s))
    """ % {"author":book.get_plain_authors(),
           "space": "  ",
           "buyer":water_mark,
           "book_id": book.id})

    result.insert(1, "\n\n")
    for page in pages:
        result.append("\n\n")
        result.append("# %s" % page.subject)
        result.append("\n\n")
        content = page.content.replace("\r", "")
        content = content.replace("{.python}", "")
        content = content.replace("{.java}", "")
        content = get_page_image(content, buy_id=buy.id)
        result.append(content)
    f.write(utf8("".join(result)))
    f.close()

    # make latex tex file by template
    mk_tex(water_mark, sell.filename, book, buy_id=buy.id)

    # latex stylesheet copy
    os.system("cp -f %(PANDOC_HOME)s/*.sty %(MD_ROOT)s" % pandoc_info)

    # book cover copy
    os.system("cp -f %(book_image_path)s %(MD_ROOT)s/%(filename)s.png" % pandoc_info)

    # epub metadata copy
    os.system("cp -f %(PANDOC_HOME)s/metadata.xml %(MD_ROOT)s" % pandoc_info)

    # make pdf
    os.system("cd %(MD_ROOT)s;pandoc --template wikidocs.tex %(filename)s.md -o %(filename)s.pdf" % pandoc_info)

    # make epub title and author information
    f = open("%(MD_ROOT)s/%(filename)s.txt" % pandoc_info, "w")
    f.write("%% %s\n" % utf8(book.subject))
    f.write("%% %s\n" % utf8(book.get_plain_authors()))
    f.close()

    # make epub
    os.system("cd %(MD_ROOT)s;pandoc --latex-engine=xelatex -H wikidocs.sty --toc --toc-depth=1 --epub-metadata=metadata.xml --epub-cover-image=%(filename)s.png %(filename)s.txt %(filename)s.md -o %(filename)s.epub" % pandoc_info)

    # make mobi
    os.system("cd %(MD_ROOT)s;ebook-convert %(filename)s.epub %(filename)s.mobi" % pandoc_info)

    # gen email directory clean
    if not os.path.exists("%(GEN_ROOT)s/%(buy_id)s" % pandoc_info):
        os.makedirs("%(GEN_ROOT)s/%(buy_id)s" % pandoc_info)
    else:
        os.system("rm -f %(GEN_ROOT)s/%(buy_id)s/*" % pandoc_info)

    # copy generated file to email directory
    os.system("cp -f %(MD_ROOT)s/%(filename)s* %(GEN_ROOT)s/%(buy_id)s" % pandoc_info)

    # buy.gen_yn = "Y"
    # buy.save()


def send_all():
    from datetime import datetime
    print "[%s] make ebook status ok.." % datetime.now()
    buy_list = Buy.objects.filter(money_yn='Y', send_yn='N')
    if buy_list:
        buy = buy_list[0]
        print "%s send_ebook start..." % buy.email
        make_ebook(buy)
        send_book(buy)
        print "%s send_ebook end." % buy.email


def send_book_by_email(email):
    buy = Buy.objects.get(email=email)
    make_ebook(buy)
    send_book(buy)

def send_book_by_buy(buy_id):
    buy = Buy.objects.get(id=buy_id)
    make_ebook(buy)
    send_book(buy)


if __name__ == "__main__":
    import django
    django.setup()
    if len(sys.argv) >= 2:
        _which_type = sys.argv[1]
        if _which_type == "email":
            email = sys.argv[2]
            send_book_by_email(email)
        elif _which_type == "buy_id":
            buy_id = sys.argv[2]
            send_book_by_buy(buy_id)
        elif _which_type == "check":
            book_id = sys.argv[2]
            check_book_by_id(book_id)
    else:
        send_all()


