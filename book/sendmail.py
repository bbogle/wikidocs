# -*- coding: utf-8 -*-

from email.mime.text import MIMEText

from django.conf import settings
import smtplib

if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
    from django.core.mail import send_mail


def sendEmail(email, subject, content):
    # send_mail(subject, content, settings.DEFAULT_FROM_EMAIL, [email])

    mailServer = smtplib.SMTP(settings.EMAIL_HOST)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    msg = MIMEText(unicode(content).encode("utf-8"), "html")
    subject = subject.replace("\r", "")
    subject = subject.replace("\n", "")
    subject = unicode(subject).encode("utf-8")
    msg["Subject"] = subject
    msg["From"] = settings.DEFAULT_FROM_EMAIL
    msg["To"] = email
    msg.set_charset('utf-8')
    mailServer.sendmail(msg["From"], msg["To"], msg.as_string())
    mailServer.quit()


if __name__ == "__main__":
    sendEmail("pahkey@gmail.com", 'test', 'content.')