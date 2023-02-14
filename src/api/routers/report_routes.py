from fastapi import APIRouter, Query, Depends, Body, Response, status

from api import schemas, dependencies
from repositories import ReportRouteRepository, ReportTypeRepository, TelegramChatRepository
from services.report_routes import group_report_routes_by_report_type_and_chat_id

router = APIRouter(prefix='/reports')


@router.get('/')
def get_report_routes(
        report_type: schemas.ReportTypeName = Query(default=None),
        chat_id: int = Query(default=None),
        limit: int = Query(default=100, ge=1, le=100),
        skip: int = Query(default=0, ge=0),
        report_routes: ReportRouteRepository = Depends(dependencies.get_report_routes_repository),
):
    report_routes_from_db = report_routes.get_all(skip=skip, limit=limit, chat_id=chat_id, report_type_name=report_type)
    return group_report_routes_by_report_type_and_chat_id(report_routes_from_db)


@router.post('/')
def create_report_route(
        report_route: schemas.ReportRoute = Body(),
        telegram_chats: TelegramChatRepository = Depends(dependencies.get_telegram_chats_repository),
        report_types: ReportTypeRepository = Depends(dependencies.get_report_types_repository),
        report_routes: ReportRouteRepository = Depends(dependencies.get_report_routes_repository),
):
    telegram_chat, _ = telegram_chats.get_or_create(chat_id=report_route.chat_id)
    report_type = report_types.get_by_name(name=report_route.report_type)
    report_routes.create(
        report_type_id=report_type.id,
        telegram_chat_id=telegram_chat.id,
        unit_ids=report_route.unit_ids,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete('/')
def delete_report_route(
        report_type: schemas.ReportTypeName = Query(),
        chat_id: int = Query(),
        unit_ids: set[schemas.UnitID] | None = Query(default=None),
        telegram_chats: TelegramChatRepository = Depends(dependencies.get_telegram_chats_repository),
        report_types: ReportTypeRepository = Depends(dependencies.get_report_types_repository),
        report_routes: ReportRouteRepository = Depends(dependencies.get_report_routes_repository),
):
    telegram_chat = telegram_chats.get_by_chat_id(chat_id=chat_id)
    report_type = report_types.get_by_name(name=report_type)
    report_routes.delete(
        report_type_id=report_type.id,
        telegram_chat_id=telegram_chat.id,
        unit_ids=unit_ids,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
