from zoneinfo import ZoneInfo

from redis import Redis

from accounts.models import AccountTokens
from accounts.services.crypt import decrypt_string
from core.services import get_redis
from reports.models.report_routes import ReportRoute
from reports.services.formatters.feedbacks import format_feedback
from reports.services.gateways.dodo_is_api import (
    get_dodo_is_api_gateway,
    OrderFeedback,
)
from telegram.services import batch_create_telegram_messages
from units.models import Unit


def is_new_feedback(
    redis: Redis,
    feedback: OrderFeedback,
) -> bool:
    key = f'feedback:{feedback.order_id.hex}'
    if not redis.exists(key):
        redis.set(key, '1')
        redis.expire(key, 60 * 60 * 24 * 3)
        return True
    return False


def is_appropriate_feedback(
    feedback: OrderFeedback,
) -> bool:
    if feedback.order_rate <= 3:
        return True
    if feedback.feedback_comment:
        return True
    return False


class CreateFeedbacksReport:
    timezone = ZoneInfo('Europe/Moscow')

    def execute(self) -> None:
        redis = get_redis()

        accounts_tokens = AccountTokens.objects.select_related(
            'account',
        ).all()

        for account_token in accounts_tokens:
            units = Unit.objects.filter(
                dodo_is_api_account_name=account_token.account.name,
            )
            unit_ids = {unit.uuid for unit in units}
            unit_id_to_name = {unit.uuid: unit.name for unit in units}

            access_token = decrypt_string(
                account_token.encrypted_access_token,
            )

            with get_dodo_is_api_gateway(
                access_token=access_token,
            ) as dodo_is_api_gateway:
                feedbacks = dodo_is_api_gateway.get_recent_feedbacks(
                    unit_ids=unit_ids,
                    include_feedbacks_with_empty_comment=True,
                )

            for feedback in feedbacks:
                if not is_appropriate_feedback(feedback):
                    continue
                if not is_new_feedback(redis, feedback):
                    continue

                unit_name = unit_id_to_name.get(feedback.unit_id, '?')
                text = format_feedback(feedback, unit_name, self.timezone)
                chat_ids = (
                    ReportRoute.objects
                    .filter(
                        report_type__name='FEEDBACKS',
                        unit__uuid=feedback.unit_id,
                    )
                    .values_list('telegram_chat__chat_id', flat=True)
                )
                batch_create_telegram_messages(
                    chat_ids=chat_ids,
                    text=text,
                )
