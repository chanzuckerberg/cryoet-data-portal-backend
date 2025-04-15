"""
GraphQL input type for limit and offset.
"""

from typing import Optional, TypedDict

import strawberry


@strawberry.input
class LimitOffsetClause(TypedDict):
    limit: Optional[int] | None
    offset: Optional[int] | None
