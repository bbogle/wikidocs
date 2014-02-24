from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import GenericSitemap

from book import views
from book.models import Book, Page

admin.autodiscover()

def get_sitemap():
    book_dict = {
        'queryset': Book.objects.filter(open_yn="Y"),
        'date_field': 'create_time',
    }

    page_dict = {
        'queryset': Page.objects.filter(book__open_yn="Y", open_yn="Y"),
        'date_field': 'modify_time',
    }

    sitemaps = {
        'docs': GenericSitemap(book_dict, priority=0.5),
        'page': GenericSitemap(page_dict, priority=0.5),
    }
    return sitemaps


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'wikidocs.views.home', name='home'),
    url(r'', include('book.urls')),
    url(r'', include('social_auth.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': get_sitemap()}),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if not settings.DEBUG:
#     urlpatterns += patterns('',
#         url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
#             {'document_root': settings.BASE_DIR+"/book/static", 'show_indexes': True})
#     )

handler404 = views.page_404
handler500 = views.page_500
