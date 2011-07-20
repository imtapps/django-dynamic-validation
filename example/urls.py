from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from sample import views

urlpatterns = patterns('',
    url(r'^$', views.Index.as_view()),
    url(r'^admin/', include(admin.site.urls)),
)
