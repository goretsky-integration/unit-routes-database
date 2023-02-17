from sqlalchemy.orm import sessionmaker

__all__ = ('BaseRepository',)


class BaseRepository:

    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory
