from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

import exceptions
import models
from db.models import Unit, Region
from repositories.base import BaseRepository

__all__ = ('UnitRepository',)


class UnitRepository(BaseRepository):

    def get_all(
            self,
            *,
            limit: int,
            skip: int,
            region_name: str | None = None,
    ) -> list[models.Unit]:
        statement = (
            select(Unit)
            .join(Unit.region)
            .limit(limit)
            .offset(skip)
            .options(joinedload(Unit.region))
            .limit(limit).offset(skip)
        )
        if region_name is not None:
            statement = statement.where(Region.name == region_name)
        with self._session_factory() as session:
            result = session.execute(statement)
            units = result.scalars().all()
        return [
            models.Unit(
                id=unit.id,
                name=unit.name,
                uuid=unit.uuid,
                office_manager_account_name=unit.office_manager_account_name,
                dodo_is_api_account_name=unit.dodo_is_api_account_name,
                region=unit.region.name,
            ) for unit in units
        ]

    def create(
            self,
            *,
            id_: int,
            name: str,
            uuid: UUID,
            office_manager_account_name: str,
            dodo_is_api_account_name: str,
            region_id: int,
    ):
        unit = Unit(
            id=id_,
            name=name,
            uuid=uuid,
            office_manager_account_name=office_manager_account_name,
            dodo_is_api_account_name=dodo_is_api_account_name,
            region_id=region_id,
        )
        try:
            with self._session_factory() as session, session.begin():
                session.add(unit)
        except IntegrityError as error:
            raise exceptions.AlreadyExistsInDatabase('Unit with this ID/name/UUID already exists')

    def get_by_name(self, name: str) -> models.Unit:
        statement = (
            select(Unit)
            .where(Unit.name == name)
            .options(joinedload(Unit.region))
        )
        with self._session_factory() as session:
            unit: Unit | None = session.scalar(statement)
        if unit is None:
            raise exceptions.DoesNotExistInDatabase('Unit by name does not exist')
        return models.Unit(
            id=unit.id,
            name=unit.name,
            uuid=unit.uuid,
            office_manager_account_name=unit.office_manager_account_name,
            dodo_is_api_account_name=unit.dodo_is_api_account_name,
            region=unit.region.name,
        )
