from fastapi import APIRouter, Depends, Query

from api import dependencies, schemas
from repositories import ReportTypeRepository

router = APIRouter(prefix='/report-types')


@router.get('/')
def get_report_types(
        limit: int = Query(default=100, ge=1, le=100),
        skip: int = Query(default=0, ge=0),
        report_types: ReportTypeRepository = Depends(dependencies.get_report_types_repository),
) -> list[schemas.ReportType]:
    return report_types.get_all(limit=limit, skip=skip, parent=None)


@router.get('/statistics/')
def get_statistics_report_types(
        limit: int = Query(default=100, ge=1, le=100),
        skip: int = Query(default=0, ge=0),
        report_types: ReportTypeRepository = Depends(dependencies.get_report_types_repository),
) -> list[schemas.ReportType]:
    return report_types.get_all(limit=limit, skip=skip, parent='STATISTICS')
