from django.conf import settings


class OnlyDebugAddChangeDeleteMixin:

    def has_delete_permission(self, request, obj=None):
        return settings.DEBUG

    def has_add_permission(self, request):
        return settings.DEBUG

    def has_change_permission(self, request, obj=None):
        return settings.DEBUG
