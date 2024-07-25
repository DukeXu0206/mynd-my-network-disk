"""mycloud URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.views import serve

from disk.urls import router

urlpatterns = [
    path('', include('disk.urls')),
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('favicon.ico', serve, {'path': 'favicon.ico'}),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + [
        path('__debug__/', include('debug_toolbar.urls'))
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = 'disk.views.bad_request_view'
handler403 = 'disk.views.permission_denied_view'
handler404 = 'disk.views.not_found_view'
handler500 = 'disk.views.server_error_view'
