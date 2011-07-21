from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

import dynamic_validation

from sample import views

admin.autodiscover()
dynamic_validation.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.Index.as_view()),
    url(r'^admin/', include(admin.site.urls)),
)
