from sqlalchemy import select
from sqlalchemy.orm import aliased

import exceptions
import models
from db.models import ReportType
from repositories.base import BaseRepository

__all__ = ('ReportTypeRepository',)


class ReportTypeRepository(BaseRepository):

    def get_by_name(self, *, name: str) -> models.ReportType:
        statement = select(ReportType).where(ReportType.name == name)
        with self._session_factory() as session:
            result = session.execute(statement)
            report_type = result.scalar()
        if report_type is None:
            raise exceptions.DoesNotExistInDatabase('Report type by this name is not found')
        return models.ReportType(id=report_type.id, name=report_type.name, verbose_name=report_type.verbose_name)

    def get_all(self, *, limit: int, skip: int, parent: str | None = None) -> list[models.ReportType]:
        statement = select(ReportType).limit(limit).offset(skip)
        if parent is None:
            statement = statement.where(ReportType.parent == parent)
        else:
            report_type_alias = aliased(ReportType)
            statement = (
                statement
                .join(ReportType.parent.of_type(report_type_alias))
                .where(report_type_alias.name == parent)
            )
        with self._session_factory() as session:
            result = session.execute(statement)
            report_types = result.scalars().all()
        return [
            models.ReportType(
                id=report_type.id,
                name=report_type.name,
                verbose_name=report_type.verbose_name,
            ) for report_type in report_types
        ]
