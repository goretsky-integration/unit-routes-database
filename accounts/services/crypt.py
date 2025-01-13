import json

from cryptography.fernet import Fernet
from django.conf import settings

__all__ = (
    'create_fernet',
    'encrypt_string',
    'decrypt_string',
    'encrypt_dict',
    'decrypt_dict',
)


def create_fernet() -> Fernet:
    return Fernet(settings.FERNET_KEY)


def encrypt_string(value: str) -> str:
    return create_fernet().encrypt(value.encode()).decode()


def decrypt_string(value: str) -> str:
    return create_fernet().decrypt(value.encode()).decode()


def encrypt_dict(value: dict) -> str:
    return create_fernet().encrypt(json.dumps(value).encode()).decode()


def decrypt_dict(value: str) -> dict:
    return json.loads(create_fernet().decrypt(value.encode()).decode())
