from dataclasses import dataclass

__all__ = ('TelegramChat',)


@dataclass
class TelegramChat:
    id: int
    chat_id: int
    title: str | None
