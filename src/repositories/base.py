from typing import TypeVar, Generic

__all__ = (
    'BaseRepository',
)

_D = TypeVar('_D')


class BaseRepository(Generic[_D]):

    def __init__(self, database: _D):
        self._database = database
