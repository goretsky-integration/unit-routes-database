from django.db import transaction

from telegram.models import TelegramChat
from user_roles.models import UserRole
from reports.models.report_routes import ReportRoute

__all__ = (
    'update_user_role',
)


@transaction.atomic
def update_user_role(*, user: TelegramChat, role: UserRole):
    user.role = role
    user.save()
    ReportRoute.objects.filter(telegram_chat=user).exclude(unit__in=role.units.all()).delete()
