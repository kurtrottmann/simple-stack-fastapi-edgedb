from typing import Any, Dict, Optional
from uuid import UUID

from edgedb import AsyncIOConnection, NoDataError
from fastapi import HTTPException

from app import utils
from app.schemas import (
    PaginatedUsers,
    User,
    UserCreate,
    UserInDB,
    UserUpdate,
    user_ordering_fields,
)
from app.security import get_password_hash, verify_password


async def get(con: AsyncIOConnection, *, id: UUID) -> Optional[User]:
    try:
        result = await con.query_one_json(
            """SELECT User {
                id,
                email,
                full_name,
                is_superuser,
                is_active,
                num_items,
                items: {
                    id,
                    title
                }
            }
            FILTER .id = <uuid>$id""",
            id=id,
        )
    except NoDataError:
        return None
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    user = User.parse_raw(result)
    return user


async def get_by_email(con: AsyncIOConnection, *, email: str) -> Optional[User]:
    try:
        result = await con.query_one_json(
            """SELECT User {
                id,
                email,
                full_name,
                is_superuser,
                is_active,
                num_items,
                items: {
                    id,
                    title
                }
            }
            FILTER .email = <str>$email""",
            email=email,
        )
    except NoDataError:
        return None
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    user = User.parse_raw(result)
    return user


async def get_multi(
    con: AsyncIOConnection,
    *,
    filtering: Dict[str, Any] = {},
    ordering: str = None,
    offset: int = 0,
    limit: int = 100,
) -> PaginatedUsers:
    filter_expr = None
    order_expr = None
    if filtering:
        filter_expr = utils.get_filter(filtering)
    if ordering:
        order_expr = utils.get_order(ordering, user_ordering_fields)
    try:
        result = await con.query_one_json(
            f"""WITH users := (
                SELECT User
                FILTER {filter_expr or 'true'}
            )
            SELECT <json>(
                count:= count(users),
                data := array_agg((
                    SELECT users {{
                        id,
                        email,
                        full_name,
                        is_superuser,
                        is_active,
                        num_items,
                        items: {{
                            id,
                            title
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
    paginated_users = PaginatedUsers.parse_raw(result)
    return paginated_users


async def create(con: AsyncIOConnection, *, obj_in: UserCreate) -> User:
    data_in = obj_in.dict(exclude_unset=True)
    if data_in.get("password"):
        data_in["hashed_password"] = get_password_hash(obj_in.password)
        del data_in["password"]
    shape_expr = utils.get_shape(data_in)
    try:
        result = await con.query_one_json(
            f"""SELECT (
                INSERT User {{
                    {shape_expr}
                }}
            ) {{
                id,
                email,
                full_name,
                is_superuser,
                is_active,
                num_items,
                items: {{
                    id,
                    title
                }}
            }}""",
            **data_in,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    user = User.parse_raw(result)
    return user


async def update(
    con: AsyncIOConnection, *, id: UUID, obj_in: UserUpdate
) -> Optional[User]:
    data_in = obj_in.dict(exclude_unset=True)
    if not data_in:
        user = await get(con, id=id)
        return user
    if data_in.get("password"):
        data_in["hashed_password"] = get_password_hash(obj_in.password)  # type: ignore
        del data_in["password"]
    shape_expr = utils.get_shape(data_in)
    try:
        result = await con.query_one_json(
            f"""SELECT (
                UPDATE User
                FILTER .id = <uuid>$id
                SET {{
                    {shape_expr}
                }}
                ) {{
                    id,
                    email,
                    full_name,
                    is_superuser,
                    is_active,
                    num_items,
                    items: {{
                        id,
                        title
                    }}
                }}""",
            id=id,
            **data_in,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    user = User.parse_raw(result)
    return user


async def remove(con: AsyncIOConnection, *, id: UUID) -> User:
    try:
        result = await con.query_one_json(
            """SELECT (
                DELETE User
                FILTER .id = <uuid>$id
            ) {
                id,
                email,
                full_name,
                is_superuser,
                is_active,
                num_items,
                items: {
                    id,
                    title
                }
            }""",
            id=id,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    user = User.parse_raw(result)
    return user


async def authenticate(
    con: AsyncIOConnection, *, email: str, password: str
) -> Optional[UserInDB]:
    try:
        result = await con.query_one_json(
            """SELECT User {
                id,
                hashed_password,
                is_active
            }
            FILTER .email = <str>$email""",
            email=email,
        )
    except NoDataError:
        return None
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    user = UserInDB.parse_raw(result)
    if not verify_password(password, user.hashed_password):
        return None
    return user
