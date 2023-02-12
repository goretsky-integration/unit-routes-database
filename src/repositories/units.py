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
        statement = select(Unit).options(joinedload(Unit.region)).limit(limit).offset(skip)
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
                account_name=unit.account_name,
                region=unit.region.name,
            ) for unit in units
        ]

    def create(
            self,
            *,
            id_: int,
            name: str,
            uuid: UUID,
            account_name: str,
            region_name: str,
    ) -> models.Unit:
        unit = Unit(id=id_, name=name, uuid=uuid, account_name=account_name, region=Region(name=region_name))
        try:
            with self._session_factory() as session, session.begin():
                session.add(unit)
        except IntegrityError as error:
            print(str(error))
            raise exceptions.AlreadyExistsInDatabase('Unit with this ID/name/UUID already exists')
        return models.Unit(
            id=unit.id,
            name=unit.id,
            uuid=unit.uuid,
            account_name=unit.account_name,
            region=unit.region.name,
        )
