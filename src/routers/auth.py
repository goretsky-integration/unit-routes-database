from fastapi import APIRouter, Depends, status

import models
from repositories import AccessTokenRepository, CookiesRepository
from routers.dependencies import (
    get_access_tokens_repository,
    get_cookies_repository,
)

router = APIRouter(prefix='/auth', tags=['Authentication credentials'])


@router.get(
    path='/token/',
    responses={
        status.HTTP_200_OK: {
            'model': models.Token,
        },
        status.HTTP_404_NOT_FOUND: {
            'content': {
                'application/json': {
                    'example': {
                        'error': 'No token by account name "your account name"',
                    },
                },
            },
        },
    },
)
async def get_access_token(
        account_name: str,
        tokens: AccessTokenRepository = Depends(get_access_tokens_repository),
):
    return await tokens.get_by_account_name(account_name)


@router.get(
    path='/cookies/',
    responses={
        status.HTTP_200_OK: {
            'model': dict[str, str],
        },
        status.HTTP_404_NOT_FOUND: {
            'content': {
                'application/json': {
                    'example': {
                        'error': 'No cookies by account name "your account name"',
                    },
                },
            },
        },
    },
)
async def get_cookies(
        account_name: str,
        cookies: CookiesRepository = Depends(get_cookies_repository),
):
    return await cookies.get_by_account_name(account_name)
