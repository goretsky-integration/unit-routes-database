from fastapi import APIRouter, Depends, status

import models
from repositories import TokensRepository, CookiesRepository
from routers.dependencies import get_tokens_repository, get_cookies_repository

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
                        'error': 'Token did not found',
                    },
                },
            },
        },
    },
)
async def get_access_token(
        account_name: str,
        tokens: TokensRepository = Depends(get_tokens_repository),
):
    return await tokens.get_by_account_name(account_name)


@router.get(
    path='/cookies/',
    responses={
        status.HTTP_200_OK: {
            'model': models.AuthCookies,
        },
        status.HTTP_404_NOT_FOUND: {
            'content': {
                'application/json': {
                    'example': {
                        'error': 'Cookies did not found',
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


@router.patch(
    path='/token/',
    status_code=status.HTTP_200_OK,
)
async def update_tokens(
        tokens_in: models.Token,
        tokens: TokensRepository = Depends(get_tokens_repository)
):
    return await tokens.update(tokens_in)


@router.patch(
    path='/cookies/',
    status_code=status.HTTP_200_OK,
)
async def update_cookies(
        cookies_in: models.AuthCookies,
        cookies: CookiesRepository = Depends(get_cookies_repository)
):
    return await cookies.update(cookies_in)
