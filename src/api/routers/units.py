from fastapi import APIRouter, Depends, Query

from api import schemas, dependencies
from repositories import UnitRepository, RegionRepository

router = APIRouter(prefix='/units')


@router.get('/')
def get_units(
        limit: int = Query(default=100, ge=1, le=100),
        skip: int = Query(default=0, ge=0),
        region: str | None = None,
        units: UnitRepository = Depends(dependencies.get_units_repository),
) -> list[schemas.Unit]:
    return units.get_all(limit=limit, skip=skip, region_name=region)


@router.post('/')
def create_unit(
        unit: schemas.Unit,
        regions: RegionRepository = Depends(dependencies.get_regions_repository),
        units: UnitRepository = Depends(dependencies.get_units_repository),
) -> schemas.Unit:
    region = regions.get_all()
    unit_created = units.create(
        id_=unit.id,
        name=unit.name,
        uuid=unit.uuid,
        account_name=unit.account_name,
        region_name=unit.region,
    )
    return unit_created


@router.get('/regions/')
def get_regions(
        regions: RegionRepository = Depends(dependencies.get_regions_repository),
) -> list[str]:
    return regions.get_all()
