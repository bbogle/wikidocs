from django.conf import settings

def book_settings(request):
    return {'DEBUG': settings.DEBUG}