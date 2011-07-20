from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(
        template_name="sample/index.html",
    ),),
    url(r'^admin/', include(admin.site.urls)),
)
