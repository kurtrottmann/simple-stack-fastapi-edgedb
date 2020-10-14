from typing import Any, Dict, Optional
from uuid import UUID

from edgedb import AsyncIOConnection, NoDataError
from fastapi import HTTPException

from app import utils
from app.schemas import (
    Item,
    ItemCreate,
    ItemUpdate,
    PaginatedItems,
    item_ordering_fields,
)


async def get(con: AsyncIOConnection, *, id: UUID) -> Optional[Item]:
    try:
        result = await con.query_one_json(
            """SELECT Item {
                id,
                title,
                description,
                owner: {
                    id,
                    email,
                    full_name
                }
            }
            FILTER .id = <uuid>$id""",
            id=id,
        )
    except NoDataError:
        return None
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    item = Item.parse_raw(result)
    return item


async def get_multi(
    con: AsyncIOConnection,
    *,
    filtering: Dict[str, Any] = {},
    ordering: str = None,
    offset: int = 0,
    limit: int = 100,
) -> PaginatedItems:
    filter_expr = None
    order_expr = None
    if filtering:
        filter_expr = utils.get_filter(filtering)
    if ordering:
        order_expr = utils.get_order(ordering, item_ordering_fields)
    try:
        result = await con.query_one_json(
            f"""WITH items := (
                SELECT Item
                FILTER {filter_expr or 'true'}
            )
            SELECT <json>(
                count:= count(items),
                data := array_agg((
                    SELECT items {{
                        id,
                        title,
                        description,
                        owner: {{
                            id,
                            email,
                            full_name
                        }}
                    }}
                    ORDER BY {order_expr or '{}'}
                    OFFSET <int64>$offset
                    LIMIT <int64>$limit
                ))
            )""",
            **filtering,
            offset=offset,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    paginated_items = PaginatedItems.parse_raw(result)
    return paginated_items


async def create(con: AsyncIOConnection, *, obj_in: ItemCreate, owner_id: UUID) -> Item:
    data_in = obj_in.dict(exclude_unset=True)
    shape_expr = utils.get_shape(data_in)
    try:
        result = await con.query_one_json(
            f"""SELECT (
                INSERT Item {{
                    {shape_expr},
                    owner := (
                        SELECT User FILTER .id = <uuid>$owner_id
                    )
                }}
            ) {{
                id,
                title,
                description,
                owner: {{
                    id,
                    email,
                    full_name
                }}
            }}""",
            **data_in,
            owner_id=owner_id,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    item = Item.parse_raw(result)
    return item


async def update(
    con: AsyncIOConnection, *, id: UUID, obj_in: ItemUpdate
) -> Optional[Item]:
    data_in = obj_in.dict(exclude_unset=True)
    if not data_in:
        item = await get(con, id=id)
        return item
    shape_expr = utils.get_shape(data_in)
    try:
        result = await con.query_one_json(
            f"""SELECT (
                UPDATE Item
                FILTER .id = <uuid>$id
                SET {{
                    {shape_expr}
                }}
            ) {{
                id,
                title,
                description,
                owner: {{
                    id,
                    email,
                    full_name
                }}
            }}""",
            id=id,
            **data_in,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    item = Item.parse_raw(result)
    return item


async def remove(con: AsyncIOConnection, *, id: UUID) -> Item:
    try:
        result = await con.query_one_json(
            """SELECT (
                DELETE Item
                FILTER .id = <uuid>$id
            ) {
                id,
                title,
                description,
                owner: {
                    id,
                    email,
                    full_name
                }
            }""",
            id=id,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    item = Item.parse_raw(result)
    return item
