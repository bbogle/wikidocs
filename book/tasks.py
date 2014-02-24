from celery import task
from pandoc.generate_ebook import make_ebook, send_book


@task
def add(x, y):
    return x + y

@task
def make_and_send(buy):
    make_ebook(buy)
    print "send book start.."
    send_book(buy)
    print "send book end."