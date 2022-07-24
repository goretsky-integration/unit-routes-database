from fastapi import APIRouter, status

router = APIRouter(prefix='/ping', tags=['Healthcheck'])


@router.get(path='/', status_code=status.HTTP_200_OK)
async def ping():
    return status.HTTP_200_OK
