from dataclasses import dataclass
from enum import IntEnum


@dataclass(frozen=True, slots=True)
class ConnectAuthorizeFormData:
    client_id: str
    redirect_uri: str
    response_type: str
    scope: str
    code_challenge: str
    code_challenge_method: str
    response_mode: str
    nonce: str
    state: str


@dataclass(frozen=True, slots=True)
class SignInOidcFormData:
    code: str
    scope: str
    state: str
    session_state: str


@dataclass(frozen=True, slots=True)
class EmptyAccountLoginFormData:
    return_url: str
    request_verification_token: str


@dataclass(frozen=True, slots=True)
class FilledAccountLoginFormData(EmptyAccountLoginFormData):
    username: str
    password: str
    tenant_name: str
    country_code: str
    auth_method: str
    remember_login: bool


@dataclass(frozen=True, slots=True)
class AccountLoginConfig:
    country_code: str
    remember_login: bool


class RoleId(IntEnum):
    SHIFT_MANAGER = 3
    OFFICE_MANAGER = 7
    ACCOUNTANT = 16


@dataclass(frozen=True, slots=True)
class SelectDepartmentFormData:
    request_verification_token: str


@dataclass(frozen=True, slots=True)
class SelectRoleFormData:
    request_verification_token: str
