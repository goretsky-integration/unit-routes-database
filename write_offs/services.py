import datetime

from django.utils import timezone
from datetime import timedelta
from write_offs.models import IngredientWriteOff


def is_10_minute_base_passed(write_off: IngredientWriteOff) -> bool:
    now = timezone.now().replace(second=0, microsecond=0)
    diff_minutes = int((now - write_off.to_write_off_at).total_seconds() // 60)
    return diff_minutes % 10 == 0


def get_write_off_status(write_off) -> str | None:
    """
    Returns a status string based on how soon the write-off is due.
    """
    now = timezone.now().replace(second=0, microsecond=0)
    delta_minutes = int((write_off.to_write_off_at - now).total_seconds() // 60)

    if delta_minutes < 0:
        if is_10_minute_base_passed(write_off):
            return "ALREADY_EXPIRED"
    elif delta_minutes <= 5:
        return "EXPIRE_AT_5_MINUTES"
    elif delta_minutes <= 10:
        return "EXPIRE_AT_10_MINUTES"
    elif delta_minutes <= 15:
        return "EXPIRE_AT_15_MINUTES"
    return None


def get_upcoming_write_offs():
    """
    Returns all unnotified write-offs that were scheduled for 5, 10, or 15 minutes
    ahead of current time — or any that were missed due to delay.
    No window used; just `lte` to ensure no silent skips.
    """
    now = datetime.datetime.now(datetime.UTC)
    target = now + timedelta(minutes=15)
    return IngredientWriteOff.objects.select_related('unit', 'ingredient').filter(
        is_notification_sent=False,
        to_write_off_at__lte=target,
    )



write_off_type_to_template = {
    'EXPIRE_AT_15_MINUTES': (
        'Списание ингредиента <b>"{ingredient_name}"</b> через 15 минут'
    ),
    'EXPIRE_AT_10_MINUTES': (
        'Списание ингредиента <b>"{ingredient_name}"</b> через 10 минут'
    ),
    'EXPIRE_AT_5_MINUTES': (
        'Списание ингредиента <b>"{ingredient_name}"</b> через 5 минут'
    ),
    'ALREADY_EXPIRED': (
        'В пиццерии просрочка ингредиента <b>"{ingredient_name}"</b>'
    ),
}


def format_write_off(write_off: IngredientWriteOff, status: str) -> str:
    template = write_off_type_to_template[status]
    event_description = template.format(ingredient_name=write_off.ingredient.name)
    return (
        f'<b>❗️ {write_off.unit.name} ❗️</b>\n'
        f'{event_description}'
    )
