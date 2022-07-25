from fastapi import APIRouter, status, Depends

import models
from routers.dependencies import get_units_repository
from repositories import UnitRepository

router = APIRouter(prefix='/units', tags=['Database'])


@router.get(
    path='/',
    status_code=status.HTTP_200_OK,
    response_model=list[models.Unit],
    response_model_by_alias=False,
)
async def get_all(
        limit: int = 100,
        skip: int = 0,
        region: models.Region | None = None,
        units: UnitRepository = Depends(get_units_repository),
):
    if region is not None:
        return await units.get_by_region(region, limit, skip)
    return await units.get_all(limit, skip)


@router.get('/regions/', status_code=status.HTTP_200_OK, response_model=list[models.Region])
async def get_regions():
    return list(models.Region)
