from django.db import transaction

from telegram.models import TelegramChat
from user_roles.models import UserRole
from reports.models.report_routes import ReportRoute

__all__ = (
    'update_user_role',
)


@transaction.atomic
def update_user_role(*, user: TelegramChat, role: UserRole | None):
    user.role = role
    user.save()
    report_routes = ReportRoute.objects.filter(telegram_chat=user)
    if role is not None:
        report_routes = report_routes.exclude(unit__in=role.units.all())
    report_routes.delete()
