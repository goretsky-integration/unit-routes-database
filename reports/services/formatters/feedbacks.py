from reports.services.gateways.dodo_is_api import OrderFeedback


def format_feedback(feedback: OrderFeedback, unit_name: str) -> str:
    exclamation = "❗️ " if feedback.order_rate == 2 else ""
    return (
        "<b>✍️ Тикеты/Отзывы с комментариями</b>\n"
        f"Время отзыва: {feedback.feedback_created_at:%d.%m.%Y %H:%M}\n"
        f"<b>{unit_name}</b>\n"
        f"<b>Заказ №{feedback.order_number}</b>\n"
        f"Время заказа: <b>{feedback.order_created_at:%d.%m.%Y %H:%M}</b>\n"
        f"Оценка: <b>{feedback.order_rate}</b> {exclamation}\n"
        f"Комментарий: <b>{feedback.feedback_comment}</b>"
    )
