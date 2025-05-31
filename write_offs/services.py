from django.utils import timezone
from datetime import timedelta
from write_offs.models import IngredientWriteOff


def get_upcoming_write_offs():
    """
    Returns write-offs that are due in exactly 15, 10, or 5 minutes and not notified yet.
    """
    now = timezone.now().replace(second=0, microsecond=0)
    target_times = [
        now + timedelta(minutes=15),
        now + timedelta(minutes=10),
        now + timedelta(minutes=5),
    ]
    return IngredientWriteOff.objects.filter(
        is_notification_sent=False,
        to_write_off_at__in=target_times,
    )


def get_expired_repeating_write_offs():
    """
    Returns expired write-offs where the minutes since `to_write_off_at` is divisible by 10
    and notification was not sent.
    """
    now = timezone.now()
    candidates = IngredientWriteOff.objects.filter(
        is_notification_sent=False,
        to_write_off_at__lte=now,
    )

    result = []
    for obj in candidates:
        diff_minutes = int((now - obj.to_write_off_at).total_seconds() // 60)
        if diff_minutes % 10 == 0:
            result.append(obj)
    return result
