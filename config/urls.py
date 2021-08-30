from django.conf import settings
from django.urls import path, include
from django.conf.urls import url
from django.contrib import admin
from django.views import static

admin.autodiscover()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('orb.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', static.serve, {'document_root': settings.MEDIA_ROOT}),
        url(r'^static/(?P<path>.*)$', static.serve,{'document_root': settings.STATIC_ROOT})
    ]

