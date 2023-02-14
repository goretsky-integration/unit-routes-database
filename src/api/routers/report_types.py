from fastapi import APIRouter, Depends, Query, Body, Response, status

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


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_report_type(
        report_type: schemas.ReportTypeCreate = Body(),
        report_types: ReportTypeRepository = Depends(dependencies.get_report_types_repository),
):
    report_types.create(name=report_type.name, verbose_name=report_type.verbose_name)
    return Response(status_code=status.HTTP_201_CREATED)


@router.post('/statistics/', status_code=status.HTTP_201_CREATED)
def create_statistics_report_type(
        report_type: schemas.ReportTypeCreate = Body(),
        report_types: ReportTypeRepository = Depends(dependencies.get_report_types_repository),
):
    statistics_report_type = report_types.get_by_name(name='STATISTICS')
    report_types.create(
        name=report_type.name,
        verbose_name=report_type.verbose_name,
        parent_id=statistics_report_type.id,
    )
    return Response(status_code=status.HTTP_201_CREATED)
