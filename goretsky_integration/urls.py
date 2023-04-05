from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('units/', include('units.urls')),
    path('telegram-chats/', include('telegram.urls')),
    path('roles/', include('user_roles.urls')),
    path('', include('reports.urls')),
)

if settings.DEBUG:
    urlpatterns.append(path('silk/', include('silk.urls', namespace='silk')))
