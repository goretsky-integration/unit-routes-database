from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('units/', include('units.urls')),
    path('telegram-chats/', include('telegram.urls')),
    path('roles/', include('user_roles.urls')),
    path('', include('accounts.urls')),
    path('', include('reports.urls')),
    path('write-offs/', include('write_offs.urls')),
    prefix_default_language=False,
)
