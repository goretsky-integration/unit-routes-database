from telegram.models import TelegramChat
from user_roles.models import UserRole

__all__ = (
    'update_user_role',
)


def update_user_role(*, user: TelegramChat, role: UserRole):
    user.role = role
    user.save()
