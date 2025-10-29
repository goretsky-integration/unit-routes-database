import time

from telegram.services import get_pending_messages, TelegramMessageSender


class SendPendingTelegramMessagesUseCase:
    def execute(self):
        messages = get_pending_messages()

        for message in messages:
            TelegramMessageSender(message=message).send()
            time.sleep(0.5)
