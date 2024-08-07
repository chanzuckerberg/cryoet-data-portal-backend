import typing
from collections import defaultdict
from typing import Any, Mapping, Optional, Sequence, Tuple
from sqlalchemy_utils.functions import get_primary_keys

from sqlalchemy.orm import RelationshipProperty
from strawberry.dataloader import DataLoader

from platformics.database.connect import AsyncDB
from platformics.graphql_api.core.errors import PlatformicsError
from platformics.graphql_api.core.query_builder import get_aggregate_db_query, get_db_query, get_db_rows
from platformics.security.authorization import AuthzAction, AuthzClient, Principal
from platformics.support import sqlalchemy_helpers

E = typing.TypeVar("E")
T = typing.TypeVar("T")


def get_input_hash(input_dict: dict) -> int:
    hash_dict = {}
    for k, v in input_dict.items():
        if isinstance(v, dict):
            v = get_input_hash(v)
        # NOTE - we're explicitly not supporting dicts inside lists since
        # our current where clause interface doesn't call for it.
        if isinstance(v, list):
            v = hash(frozenset(v))
        hash_dict[k] = v
    return hash(tuple(sorted(hash_dict.items())))


class EntityLoader:
    """
    Creates DataLoader instances on-the-fly for SQLAlchemy relationships
    """

    _loaders: dict[RelationshipProperty, DataLoader]
    _aggregate_loaders: dict[RelationshipProperty, DataLoader]

    def __init__(self, engine: AsyncDB, authz_client: AuthzClient, principal: Principal) -> None:
        self._loaders = {}
        self._aggregate_loaders = {}
        self.engine = engine
        self.authz_client = authz_client
        self.principal = principal

    async def resolve_nodes(self, cls: Any, node_ids: list[str]) -> Sequence[E]:
        """
        Given a list of node IDs from a Relay `node()` query, return corresponding entities
        """
        db_session = self.engine.session()
        # What's the class identifier?

        pk_col_name, _ = sqlalchemy_helpers.get_primary_key(cls)
        if pk_col_name is None:
            raise Exception("Primary keys are required for each class")
        where = {pk_col_name: {"_in": node_ids}}
        rows = await get_db_rows(cls, db_session, self.authz_client, self.principal, where)
        await db_session.close()
        return rows

    def loader_for(
        self,
        relationship: RelationshipProperty,
        where: Optional[Any] = None,
        order_by: Optional[Any] = None,
    ) -> DataLoader:
        """
        Retrieve or create a DataLoader for the given relationship
        """
        if not where:
            where = {}
        if not order_by:
            order_by = []

        input_dict = {}  # type: ignore
        input_dict.update(where)
        for item in order_by:
            input_dict.update(item)
        input_hash = get_input_hash(input_dict)

        try:
            return self._loaders[(relationship, input_hash)]  # type: ignore
        except KeyError:
            related_model = relationship.entity.entity

            async def load_fn(keys: list[Any]) -> typing.Sequence[Any]:
                if not relationship.local_remote_pairs:
                    raise Exception("invalid relationship")
                filters = []
                for _, remote in relationship.local_remote_pairs:
                    filters.append(remote.in_(keys))
                query = get_db_query(
                    related_model,
                    AuthzAction.VIEW,
                    self.authz_client,
                    self.principal,
                    where,
                    order_by,  # type: ignore
                    relationship,  # type: ignore
                )
                for item in filters:
                    query = query.where(item)
                db_session = self.engine.session()
                rows = (await db_session.execute(query)).scalars().all()
                await db_session.close()

                def group_by_remote_key(row: Any) -> Tuple:
                    if not relationship.local_remote_pairs:
                        raise Exception("invalid relationship")
                    # TODO -- Technically, SA supports multiple field filters in a relationship! We'll need to handle this case
                    return [getattr(row, remote.key) for _, remote in relationship.local_remote_pairs if remote.key][0]

                grouped_keys: Mapping[Any, list[Any]] = defaultdict(list)
                for row in rows:
                    grouped_keys[group_by_remote_key(row)].append(row)
                if relationship.uselist:
                    return [grouped_keys[key] for key in keys]
                else:
                    return [grouped_keys[key][0] if grouped_keys[key] else None for key in keys]

            self._loaders[(relationship, input_hash)] = DataLoader(load_fn=load_fn)  # type: ignore
            return self._loaders[(relationship, input_hash)]  # type: ignore

    def aggregate_loader_for(
        self,
        relationship: RelationshipProperty,
        where: Optional[Any] = None,
        selections: Optional[Any] = None,
    ) -> DataLoader:
        """
        Retrieve or create a DataLoader that aggregates data for the given relationship
        """
        if not where:
            where = {}
        if not selections:
            selections = []

        input_hash = get_input_hash(where)
        str_selections = str(selections)

        try:
            return self._aggregate_loaders[(relationship, str_selections, input_hash)]  # type: ignore
        except KeyError:
            related_model = relationship.entity.entity

            async def load_fn(keys: list[Any]) -> typing.Sequence[Any]:
                if not relationship.local_remote_pairs:
                    raise Exception("invalid relationship")
                filters = []
                for _, remote in relationship.local_remote_pairs:
                    filters.append(remote.in_(keys))
                order_by: list = []
                if relationship.order_by:
                    order_by = [relationship.order_by]

                if selections:
                    aggregate_selections = [selection for selection in selections if selection.name != "groupBy"]
                    groupby_selections = [selection for selection in selections if selection.name == "groupBy"]
                    groupby_selections = groupby_selections[0].selections if groupby_selections else []
                else:
                    aggregate_selections = []
                    groupby_selections = []
                if not aggregate_selections:
                    raise PlatformicsError("No aggregate functions selected")

                query, group_by = get_aggregate_db_query(
                    related_model,
                    AuthzAction.VIEW,
                    self.authz_client,
                    self.principal,
                    where,
                    aggregate_selections,
                    groupby_selections,
                    None,
                    remote,  # type: ignore
                )
                for item in filters:
                    query = query.where(item)
                for item in order_by:
                    query = query.order_by(item)
                if group_by:
                    query = query.group_by(*group_by)  # type: ignore
                db_session = self.engine.session()
                rows = (await db_session.execute(query)).mappings().all()
                await db_session.close()

                def group_by_remote_key(row: Any) -> Tuple:
                    if not relationship.local_remote_pairs:
                        raise Exception("invalid relationship")
                    # TODO -- Technically, SA supports multiple field filters in a relationship! We'll need to handle this case
                    return [row[remote.key] for _, remote in relationship.local_remote_pairs if remote.key][0]

                grouped_keys: Mapping[Any, list[Any]] = defaultdict(list)
                for row in rows:
                    grouped_keys[group_by_remote_key(row)].append(row)
                if relationship.uselist:
                    return [grouped_keys[key] for key in keys]
                else:
                    return [grouped_keys[key][0] if grouped_keys[key] else None for key in keys]

            self._aggregate_loaders[(relationship, str_selections, input_hash)] = DataLoader(load_fn=load_fn)  # type: ignore
            return self._aggregate_loaders[(relationship, str_selections, input_hash)]  # type: ignore
