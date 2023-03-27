from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('units/', include('units.urls')),
    path('telegram-chats/', include('telegram.urls')),
    path('', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns.append(path('silk/', include('silk.urls', namespace='silk')))
