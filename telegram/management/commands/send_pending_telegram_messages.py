from django.core.management import BaseCommand

from telegram.use_cases.send_pending_telegram_messages import (
    SendPendingTelegramMessagesUseCase,
)


class Command(BaseCommand):

    def handle(self, *args, **options):
        SendPendingTelegramMessagesUseCase().execute()
        self.stdout.write(
            self.style.SUCCESS('Successfully sent pending messages'),
        )
