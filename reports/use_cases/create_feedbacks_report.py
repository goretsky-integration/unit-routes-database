from collections.abc import Iterable

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


class FeedbacksFilter:

    def __init__(self, redis: Redis) -> None:
        self.__redis = redis
        self.__new_feedback_ids: set[str] = set()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.rewrite_cache()

    def filter(self, feedbacks: Iterable[OrderFeedback]) -> list[
        OrderFeedback]:
        result: list[OrderFeedback] = []

        for feedback in feedbacks:
            if feedback.order_rate > 3 and not feedback.feedback_comment:
                continue
            if not self.__redis.sismember('feedbacks', feedback.order_id.hex):
                result.append(feedback)
                self.__new_feedback_ids.add(feedback.order_id.hex)

        return result

    def rewrite_cache(self) -> None:
        if not self.__new_feedback_ids:
            return

        self.__redis.delete('feedbacks')
        self.__redis.sadd('feedbacks', *self.__new_feedback_ids)


class CreateFeedbacksReport:

    def execute(self) -> None:
        redis = get_redis()

        with FeedbacksFilter(redis) as feedbacks_filter:
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

                feedbacks = feedbacks_filter.filter(feedbacks)

                for feedback in feedbacks:
                    unit_name = unit_id_to_name.get(feedback.unit_id, '?')
                    text = format_feedback(feedback, unit_name)
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
