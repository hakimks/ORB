from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views import static

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('orb.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', static.serve, {'document_root': settings.MEDIA_ROOT}),
        url(r'^static/(?P<path>.*)$', static.serve,{'document_root': settings.STATIC_ROOT})
    ]

