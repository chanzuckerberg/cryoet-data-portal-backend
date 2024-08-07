import typing
from enum import Enum

from cerbos.sdk.client import CerbosClient
from cerbos.sdk.model import Principal as CerbosPrincipal
from cerbos.sdk.model import Resource, ResourceDesc
from sqlalchemy.sql import Select

import platformics.database.models as db
from platformics.security.token_auth import get_token_claims
from platformics.settings import APISettings
from platformics.thirdparty.cerbos_sqlalchemy.query import get_query


class AuthzAction(str, Enum):
    VIEW = "view"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


# TODO - right now this is an unmodified alias of Cerbos' principal, but we can extend it in the future
# if need be. The properties/methods of this class are *only* referenced in this file!
class Principal(CerbosPrincipal):
    pass


def hydrate_auth_principal(
    settings: APISettings,
    user_token: typing.Optional[str],
) -> typing.Optional[Principal]:
    if not user_token:
        return None
    try:
        claims = get_token_claims(settings.JWK_PRIVATE_KEY, user_token)
    except:  # noqa
        return None

    if "project_roles" not in claims:
        raise Exception("no project roles in claims")

    project_claims = claims["project_roles"]

    try:
        for role, project_ids in project_claims.items():
            assert role in ["member", "owner", "viewer"]
            assert isinstance(project_ids, list)
            for item in project_ids:
                assert int(item)
    except Exception:
        return None

    return Principal(
        claims["sub"],
        roles=["user"],
        attr={
            "user_id": int(claims["sub"]),
            "owner_projects": project_claims.get("owner", []),
            "member_projects": project_claims.get("member", []),
            "viewer_projects": project_claims.get("viewer", []),
            "service_identity": claims["service_identity"],
        },
    )


class AuthzClient:
    def __init__(self, settings: APISettings):
        self.settings = settings
        self.client = CerbosClient(host=settings.CERBOS_URL)

    # Convert a model object to a dictionary
    def _obj_to_dict(self, obj):
        mydict = {}
        relationships = obj.__mapper__.relationships
        for col in obj.__mapper__.all_orm_descriptors:
            # Don't send related fields to cerbos for authz checks
            if col.key in relationships:
                continue
            value = getattr(obj, col.key)
            if type(value) not in [int, str, bool, float]:
                # TODO, we probably want to look into a smarter way to serialize fields for cerbos
                value = str(value)
            mydict[col.key] = value
        return mydict

    # get a list of non-relationship cols for a model class
    def _model_class_cols(self, cls):
        cols = []
        relationships = cls.__mapper__.relationships
        for col in cls.__mapper__.all_orm_descriptors:
            # Don't send related fields to cerbos for authz checks
            if col.key in relationships:
                continue
            cols.append(col)
        return cols

    def can_create(self, resource, principal: Principal) -> bool:
        resource_type = type(resource).__tablename__
        attr = self._obj_to_dict(resource)
        resource = Resource(id="NEW_ID", kind=resource_type, attr=attr)
        if self.client.is_allowed(AuthzAction.CREATE, principal, resource):
            return True
        return False

    def can_update(self, resource, principal: Principal) -> bool:
        resource_type = type(resource).__tablename__
        attr = self._obj_to_dict(resource)
        # TODO - this should send in the actual resource ID instead of a placeholder string
        # There are two complexities there though: UUID's don't natively serialize to json,
        # so they cannot be sent in cerbos perms checks, and we need to find/use the table's
        # primary key instead of a hardcoded column name.
        resource = Resource(id="resource_id", kind=resource_type, attr=attr)
        if self.client.is_allowed(AuthzAction.UPDATE, principal, resource):
            return True
        return False

    # Get a SQLAlchemy model with authz filters already applied
    def get_resource_query(
        self,
        principal: Principal,
        action: AuthzAction,
        model_cls: type[db.Base],  # type: ignore
        relationship: typing.Optional[typing.Any] = None,  # type: ignore
    ) -> Select:
        rd = ResourceDesc(model_cls.__tablename__)
        plan = self.client.plan_resources(action, principal, rd)

        attr_map = {}
        joins = []
        if model_cls == db.File:  # type: ignore
            if not relationship:
                raise Exception("Relationship is required for File queries")
            parent = relationship.parent.entity
            joins = [(parent, relationship.primaryjoin)]

            for col in self._model_class_cols(parent):
                attr_map[f"request.resource.attr.{col.key}"] = getattr(parent, col.key)
        else:
            # Send all non-relationship columns to cerbos to make decisions
            for col in self._model_class_cols(model_cls):
                attr_map[f"request.resource.attr.{col.key}"] = getattr(model_cls, col.key)
        query = get_query(
            plan,
            model_cls,  # type: ignore
            attr_map,  # type: ignore
            joins,  # type: ignore
        )
        return query

    # An opportunity to modify SQL WHERE clauses before they get sent to the DB.
    def modify_where_clause(
        self,
        principal: Principal,
        action: AuthzAction,
        model_cls: type[db.Base],  # type: ignore
        where_clauses: dict[str, typing.Any],
    ):
        pass
