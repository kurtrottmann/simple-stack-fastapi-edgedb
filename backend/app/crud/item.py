from typing import Optional
from uuid import UUID

from edgedb import AsyncIOConnection, NoDataError

from app import db
from app.schemas import Item, ItemCreate, ItemUpdate, PaginatedItems


async def get(con: AsyncIOConnection, *, id: UUID) -> Optional[Item]:
    try:
        result = await con.fetchone_json(
            """SELECT Item {
                id,
                title,
                description,
                owner: { id, full_name, email }
            }
            FILTER .id = <uuid>$id""",
            id=id,
        )
    except NoDataError:
        return None
    except Exception as e:
        print(f"EXCEPTION: {e}")
    item = Item.parse_raw(result)
    return item


async def get_multi(
    con: AsyncIOConnection, *, skip: int = 0, limit: int = 100
) -> PaginatedItems:
    try:
        result = await con.fetchone_json(
            """SELECT <json>(
                count:= count(Item),
                data := array_agg((
                    SELECT Item {
                        id,
                        title,
                        description,
                        owner: { id, full_name, email }
                    }
                    OFFSET <int64>$offset
                    LIMIT <int64>$limit
                ))
            )""",
            offset=skip,
            limit=limit,
        )
    except Exception as e:
        print(f"EXCEPTION: {e}")
    paginated_items = PaginatedItems.parse_raw(result)
    return paginated_items


async def get_multi_by_owner(
    con: AsyncIOConnection, *, owner_id: UUID, skip: int = 0, limit: int = 100
) -> PaginatedItems:
    try:
        result = await con.fetchone_json(
            """WITH items := (
                SELECT Item
                FILTER .owner.id = <uuid>$id
            )
            SELECT <json>(
                count:= count(items),
                data := array_agg((
                    SELECT items {
                        id,
                        title,
                        description,
                        owner: { id, full_name, email }
                    }
                    OFFSET <int64>$offset
                    LIMIT <int64>$limit
                ))
            )""",
            id=id,
            offset=skip,
            limit=limit,
        )
    except Exception as e:
        print(f"EXCEPTION: {e}")
    paginated_items = PaginatedItems.parse_raw(result)
    return paginated_items


async def create(con: AsyncIOConnection, *, obj_in: ItemCreate) -> Item:
    try:
        result = await con.fetchone_json(
            """SELECT (
                INSERT Item {
                    title := <str>$title,
                    description := <str>$description,
                }
            ) {
                id,
                title,
                description,
                owner: { id, full_name, email }
            }""",
            title=obj_in.title,
            description=obj_in.description,
        )
    except Exception as e:
        print(f"EXCEPTION: {e}")
    item = Item.parse_raw(result)
    return item


async def create_with_owner(
    con: AsyncIOConnection, *, obj_in: ItemCreate, owner_id: UUID
) -> Item:
    try:
        result = await con.fetchone_json(
            """SELECT (
                INSERT Item {
                    title := <str>$title,
                    description := <str>$description,
                    owner := (
                        SELECT User FILTER .id = <uuid>$owner_id
                    )
                }
            ) {
                id,
                title,
                description,
                owner: { id, full_name, email }
            }""",
            title=obj_in.title,
            description=obj_in.description,
            owner_id=owner_id,
        )
    except Exception as e:
        print(f"EXCEPTION: {e}")
    item = Item.parse_raw(result)
    return item


async def update(con: AsyncIOConnection, *, db_obj: Item, obj_in: ItemUpdate) -> Item:
    update_data = obj_in.dict(exclude_unset=True, exclude={"owner_id"})
    shape = ", ".join([k + db.type_cast(update_data[k]) + k for k in update_data])
    if obj_in.owner_id:
        shape += f", owner := (SELECT User FILTER .id = <uuid>'{obj_in.owner_id}')"
    try:
        result = await con.fetchone_json(
            f"""SELECT (
                UPDATE Item
                FILTER .id = <uuid>$id
                SET {{ {shape} }}
            ) {{
                id,
                title,
                description,
                owner: {{ id, full_name, email }}
            }}""",
            id=db_obj.id,
            **update_data,
        )
    except Exception as e:
        print(f"EXCEPTION: {e}")
    item = Item.parse_raw(result)
    return item


async def remove(con: AsyncIOConnection, *, id: UUID) -> Item:
    try:
        result = await con.fetchone_json(
            """SELECT (
                DELETE Item
                FILTER .id = <uuid>$id
            ) {
                id,
                title,
                description,
                owner: { id, full_name, email }
            }""",
            id=id,
        )
    except Exception as e:
        print(f"EXCEPTION: {e}")
    item = Item.parse_raw(result)
    return item
