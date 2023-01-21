from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache

import models
from repositories import ReportTypeRepository, StatisticsReportTypeRepository
from routers.dependencies import get_report_types_repository, get_statistics_report_types_repository

router = APIRouter(prefix='/report-types', tags=['Database'])


@router.get(
    path='/',
    response_model=list[models.ReportType],
    response_model_by_alias=False,
)
@cache(expire=600)
async def get_report_types(
        skip: int = 0,
        limit: int = 100,
        report_types: ReportTypeRepository = Depends(get_report_types_repository),
):
    return await report_types.get_all(skip, limit)


@router.get(
    path='/statistics/',
    response_model=list[models.StatisticsReportType],
    response_model_by_alias=False,
)
@cache(expire=600)
async def get_statistics_report_types(
        skip: int = 0,
        limit: int = 100,
        statistics_report_types: StatisticsReportTypeRepository = Depends(get_statistics_report_types_repository),
):
    return await statistics_report_types.get_all(skip, limit)
