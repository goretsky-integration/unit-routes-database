from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UserRolesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_roles'
    verbose_name = _('user_roles|app')
