from django.conf.urls import patterns, include, url
from uuweb.settings import MEDIA_ROOT
from uupictures import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'uuweb.views.home', name='home'),
    # url(r'^uuweb/', include('uuweb.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.index),
    url(r'^/$', views.index),

    url(r'^superstar/$', views.superstar),
    url(r'^food/$', views.food),
    url(r'^cartoon/$', views.cartoon),
    url(r'^travel/$', views.travel),
    url(r'^photography/$', views.photography),
    url(r'^design/$', views.design),
    url(r'^funny/$', views.funny),
    url(r'^car/$', views.car),

    url(r'^superstar/(?P<currentPage>\d*)/$', views.superstar),
    url(r'^food/(?P<currentPage>\d*)/$', views.food),
    url(r'^cartoon/(?P<currentPage>\d*)/$', views.cartoon),
    url(r'^travel/(?P<currentPage>\d*)/$', views.travel),
    url(r'^photography/(?P<currentPage>\d*)/$', views.photography),
    url(r'^design/(?P<currentPage>\d*)/$', views.design),
	url(r'^funny/(?P<currentPage>\d*)/$', views.funny),
	url(r'^car/(?P<currentPage>\d*)/$', views.car),

	url(r'^detail/(?P<id>\d+)/$', views.detail),

    url(r'^comments_diaplay/$',views.commentsDisplay),
    url(r'^comments/(?P<picId>\d+)/(?P<userId>\d+)',views.comments),
    url(r'^comments_like/$',views.commentsLike),
    url(r'^comments_unlike/$',views.commentsUnlike),


	url(r'^login/$', views.login),
    url(r'^login/emailunique/$', views.emailUnique),
	url(r'^logout/$', views.logout),
    url(r'^register/$', views.register),
    url(r'^register/submit/$', views.submit),

    url(r'^captcha/\d*$', views.captcha),
    url(r'^checkcaptcha/', views.checkCaptcha),

    url(r'^mygallery/(?P<id>\d+)/(?P<currentPage>\d*)/$', views.myGallery),
    url(r'^mygallery/(?P<id>\d+)/$', views.myGallery),
    url(r'^user_edit_pic/(?P<id>\d+)/$', views.userEditPic),
    url(r'^del_pic/(?P<id>\d+)/$', views.delPic),
    url(r'^upload/$', views.upload),
    url(r'^upload_pic_form/', views.uploadPicForm),
    url(r'^upload/pic/(?P<id>\d+)/$',views.uploadPic),

    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': MEDIA_ROOT}),
)
