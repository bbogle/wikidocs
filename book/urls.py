from django.conf.urls import patterns, url

from book import views
from book import auth_views as auth
from book import old_views as old

urlpatterns = patterns('',
    # index
    url(r'^$', views.index, name='index'),
    url(r'^tab/(\w+)$', views.index_tab),

    # book
    url(r'^book/(\d+)$', views.book, name='book'),
    url(r'^book/recommend/(\d+)$', views.book_recommend),
    url(r'^book/comment/save$', views.book_comment_save),
    url(r'^book/comment/remove', views.book_comment_remove),
    url(r'^buy/(\d+)$', views.buy),
    url(r'^buy/save$', views.buy_save),

    # page
    url(r'^(\d+)$', views.page, name='page'),
    url(r'^page/comment/save$',         views.page_comment_save),
    url(r'^page/comment/edit/(\d+)$',   views.page_comment_edit),
    url(r'^page/comment/remove',        views.page_comment_remove),

    # edit
    url(r'^edit/book/(\d+)$', views.edit_book),
    url(r'^edit/book/save$', views.edit_book_save),
    url(r'^edit/book/new$', views.edit_book_new),
    url(r'^edit/book/user$', views.edit_book_user),
    url(r'^edit/book/user/add$', views.edit_book_user_add),
    url(r'^edit/book/user/del$', views.edit_book_user_del),

    url(r'^edit/page/(\d+)$', views.edit_page),
    url(r'^edit/page/save$', views.edit_page_save),
    url(r'^edit/page/new/(\d+)$', views.edit_page_new),
    url(r'^edit/page/image/upload$', views.edit_page_image_upload),
    url(r'^edit/page/image/del$', views.edit_page_image_del),
    url(r'^edit/preview$', views.edit_preview),

    # profile
    url(r'^profile/(\d+)$', 'book.profile_views.info'),
    url(r'^profile/edit/base$', 'book.profile_views.edit_base'),
    url(r'^profile/edit/password$', 'book.profile_views.edit_password'),

    # help
    url(r'^help/(\w+)$', views.help),

    # feedback
    url(r'^feedback$', views.feedback),

    # --------------------------------------------

    # authentication
    url(r'^loginForm$', auth.loginForm),
    url(r'^logout$', auth.logout),
    url(r'^joinForm$', auth.joinForm),
    url(r'^login$', auth.login),
    url(r'^join$', auth.join),
    url(r'^passwdForm$', auth.passwdForm),
    url(r'^passwd/send$', auth.passwd_send),

    # social login
    url(r'^login/auth$', auth.social_auth),
    url(r'^login/auth/error$', auth.social_auth_error),

    # old
    url(r'^read', views.index),

    # old api
    url(r'^api/page/(\d+)$', old.api_page),
    url(r'^api/toc$', old.api_toc),
    url(r'^api/comment$', old.api_comment),
)
