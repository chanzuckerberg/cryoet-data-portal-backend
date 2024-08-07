from typing import Any, Optional

from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker


class AsyncDB:
    def __init__(self, engine: AsyncEngine):
        self._engine = engine
        self._session_maker: Optional[async_sessionmaker[AsyncSession]] = None

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    @property
    def session(self) -> async_sessionmaker[AsyncSession]:
        if not self._session_maker:
            session = async_sessionmaker(self._engine, expire_on_commit=False)
            self._session_maker = session
        return self._session_maker


class SyncDB:
    def __init__(self, engine: Engine):
        self._engine = engine
        self._session_maker: Optional[sessionmaker[Session]] = None

    @property
    def engine(self) -> Engine:
        return self._engine

    @property
    def session(self) -> sessionmaker[Session]:
        if not self._session_maker:
            session = sessionmaker(bind=self._engine, expire_on_commit=False)
            self._session_maker = session
        return self._session_maker


def init_async_db(db_uri: str, **kwargs: dict[str, Any]) -> AsyncDB:
    engine = create_async_engine(db_uri, pool_size=5, max_overflow=5, future=True, **kwargs)
    return AsyncDB(engine)


def init_sync_db(db_uri: str, **kwargs: dict[str, Any]) -> SyncDB:
    engine = create_engine(db_uri, **kwargs)
    return SyncDB(engine)
