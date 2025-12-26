from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/units/', include('units.urls')),
    path('api/telegram-chats/', include('telegram.urls')),
    path('api/roles/', include('user_roles.urls')),
    path('api/', include('accounts.urls')),
    path('api/', include('reports.urls')),
    path('api/write-offs/', include('write_offs.urls')),
]
