from sqlalchemy import select

import exceptions
import models
from db.models import Region
from repositories.base import BaseRepository


class RegionRepository(BaseRepository):

    def get_all(self) -> list[str]:
        statement = select(Region)
        with self._session_factory() as session:
            result = session.execute(statement)
            regions = result.scalars().all()
        return [region.name for region in regions]

    def get_by_name(self, *, name: str) -> models.Region:
        statement = select(Region).where(Region.name == name)
        with self._session_factory() as session:
            result = session.execute(statement)
            region = result.scalar()
        if region is None:
            raise exceptions.DoesNotExistInDatabase('Region is not found')
        return models.Region(id=region.id, name=region.name)
