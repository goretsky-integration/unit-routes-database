from fastapi import APIRouter
from fastapi.params import Depends

import models
from repositories import AccountRepository
from routers.dependencies import get_accounts_repository

router = APIRouter(prefix='/accounts', tags=['Database'])


@router.get(path='/', response_model=list[models.Account])
async def get_all(
        skip: int = 0,
        limit: int = 100,
        accounts: AccountRepository = Depends(get_accounts_repository),
):
    return await accounts.get_all(skip, limit)
