from typing import Iterable

from sqlalchemy import select, delete, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

import exceptions
import models
from db.models import ReportRoute, TelegramChat, ReportType
from repositories.base import BaseRepository

__all__ = ('ReportRouteRepository',)


class ReportRouteRepository(BaseRepository):

    def get_all(
            self,
            *,
            skip: int,
            limit: int,
            report_type_name: str | None = None,
            chat_id: int | None = None,
    ) -> list[models.ReportRoute]:
        statement = (
            select(ReportRoute)
            .options(joinedload(ReportRoute.telegram_chat))
            .options(joinedload(ReportRoute.report_type))
            .limit(limit)
            .offset(skip)
        )
        if report_type_name is not None:
            statement = statement.where(ReportType.name == report_type_name)
        if chat_id is not None:
            statement = statement.where(TelegramChat.chat_id == chat_id)
        with self._session_factory() as session:
            result = session.execute(statement)
            report_routes = result.scalars().all()
        return [
            models.ReportRoute(
                report_type_name=report_route.report_type.name,
                telegram_chat_id=report_route.telegram_chat.chat_id,
                unit_id=report_route.unit_id
            ) for report_route in report_routes
        ]

    def create(
            self,
            *,
            report_type_id: int,
            telegram_chat_id: int,
            unit_ids: Iterable[int],
    ):
        report_routes = [
            ReportRoute(
                telegram_chat_id=telegram_chat_id,
                report_type_id=report_type_id,
                unit_id=unit_id,
            ) for unit_id in unit_ids
        ]
        try:
            with self._session_factory() as session, session.begin():
                session.add_all(report_routes)
        except IntegrityError as error:
            if 'is not present in table' in str(error):
                raise exceptions.DoesNotExistInDatabase('Unit is not found')
            raise exceptions.AlreadyExistsInDatabase(
                'Report route with this combination of unit ID,'
                ' telegram chat ID and report type already exists'
            )

    def delete(
            self,
            *,
            report_type_id: int,
            telegram_chat_id: int,
            unit_ids: Iterable[int] | None = None,
    ) -> None:
        statement = (
            delete(ReportRoute)
            .where(
                ReportRoute.report_type_id == report_type_id,
                ReportRoute.telegram_chat_id == telegram_chat_id,
            )
        )
        if unit_ids is not None:
            statement = statement.where(ReportRoute.unit_id.in_(unit_ids))
        with self._session_factory() as session, session.begin():
            result = session.execute(statement)
        is_deleted = result.rowcount > 0
        if not is_deleted:
            raise exceptions.DoesNotExistInDatabase('Report route is not found')

    async def get_chat_ids_and_unit_ids_by_report_type(
            self, report_type: str,
    ) -> list[models.ReportChatIdAndUnitIds]:
        query = self._database.find({'report_type': report_type}, {'report_type': 0, '_id': 0})
        return [models.ReportChatIdAndUnitIds.parse_obj(report) async for report in query]
