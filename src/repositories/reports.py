from typing import Iterable

import models
from repositories.base import BaseRepository

__all__ = (
    'ReportRepository',
)


def construct_predicate_and(predicates: list[dict]) -> dict:
    if not predicates:
        return {}
    if len(predicates) == 1:
        return predicates[0]
    return {'$and': predicates}


class ReportRepository(BaseRepository):

    async def get_all(
            self,
            skip: int,
            limit: int,
            report_type: models.ReportType | None = None,
            chat_id: int | None = None,
    ) -> list[models.Report]:
        predicates = []
        if report_type is not None:
            predicates.append({'report_type': report_type})
        if chat_id is not None:
            predicates.append({'chat_id': chat_id})
        query = self._database.find(construct_predicate_and(predicates), {'_id': 0}).skip(skip).limit(limit)
        return [models.Report.parse_obj(report) async for report in query]

    async def upsert_unit_id(self, report_type: models.ReportType, chat_id: int, unit_ids: Iterable[int]):
        await self._database.update_one(
            {'$and': [{'report_type': report_type}, {'chat_id': chat_id}]},
            {'$addToSet': {'unit_ids': {'$each': unit_ids}}},
            upsert=True,
        )

    async def delete_unit_id(self, report_type: models.ReportType, chat_id: int, unit_ids: Iterable[int]):
        await self._database.update_one(
            {'$and': [{'report_type': report_type}, {'chat_id': chat_id}]},
            {'$pull': {'unit_ids': {'$in': unit_ids}}},
        )

    async def get_chat_ids_and_unit_ids_by_report_type(
            self, report_type: str,
    ) -> list[models.ReportChatIdAndUnitIds]:
        query = self._database.find({'report_type': report_type}, {'report_type': 0, '_id': 0})
        return [models.ReportChatIdAndUnitIds.parse_obj(report) async for report in query]
