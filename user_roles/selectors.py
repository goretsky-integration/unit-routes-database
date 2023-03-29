from user_roles.models import UserRole
from core.exceptions import NotFoundError


def get_role(access_code: str) -> UserRole:
    try:
        return UserRole.objects.get(access_code=access_code)
    except UserRole.DoesNotExist:
        raise NotFoundError('Role is not found')
