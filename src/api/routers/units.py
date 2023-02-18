from fastapi import APIRouter, Depends, Query, status, Response, Body

from api import schemas, dependencies
from repositories import UnitRepository, RegionRepository

router = APIRouter(prefix='/units')


@router.get(
    path='/',
    status_code=status.HTTP_200_OK,
)
def get_units(
        limit: int = Query(default=100, ge=1, le=100),
        skip: int = Query(default=0, ge=0),
        region: str | None = None,
        units: UnitRepository = Depends(dependencies.get_units_repository),
) -> list[schemas.Unit]:
    return units.get_all(limit=limit, skip=skip, region_name=region)


@router.get('/name/{name}/', status_code=status.HTTP_200_OK)
def get_unit_by_name(
        name: str,
        units: UnitRepository = Depends(dependencies.get_units_repository),
) -> schemas.Unit:
    return units.get_by_name(name)


@router.post('/')
def create_unit(
        unit: schemas.Unit,
        regions: RegionRepository = Depends(dependencies.get_regions_repository),
        units: UnitRepository = Depends(dependencies.get_units_repository),
):
    region = regions.get_by_name(name=unit.region)
    units.create(
        id_=unit.id,
        name=unit.name,
        uuid=unit.uuid,
        account_name=unit.account_name,
        region_id=region.id,
    )
    return Response(status_code=status.HTTP_201_CREATED)


@router.get('/regions/')
def get_regions(
        regions: RegionRepository = Depends(dependencies.get_regions_repository),
) -> list[str]:
    return regions.get_all()


@router.post('/regions/')
def create_regions(
        region: schemas.RegionCreate = Body(),
        regions: RegionRepository = Depends(dependencies.get_regions_repository),
):
    return regions.create(name=region.name)
