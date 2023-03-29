from django.contrib import admin
from django.contrib.auth.models import User, Group

from django.conf import settings

if not settings.DEBUG:
    admin.site.unregister(User)
    admin.site.unregister(Group)
