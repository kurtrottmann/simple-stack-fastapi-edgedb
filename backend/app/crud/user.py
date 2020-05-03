from typing import Optional
from uuid import UUID

from edgedb import AsyncIOConnection, NoDataError

from app import db
from app.schemas import PaginatedUsers, User, UserCreate, UserInDB, UserUpdate
from app.security import get_password_hash, verify_password


async def get(con: AsyncIOConnection, *, id: UUID) -> Optional[User]:
    try:
        result = await con.fetchone_json(
            """SELECT User {
                    id,
                    full_name,
                    email,
                    is_superuser,
                    is_active,
                    num_items := count(.<owner[IS Item]),
                    items:= .<owner[IS Item] { id, title }
            }
            FILTER .id = <uuid>$id""",
            id=id,
        )
    except NoDataError:
        return None
    except Exception as e:
        print(f"EXCEPTION: {e}")
    user = User.parse_raw(result)
    return user


async def get_by_email(con: AsyncIOConnection, *, email: str) -> Optional[User]:
    try:
        result = await con.fetchone_json(
            """SELECT User {
                    id,
                    full_name,
                    email,
                    is_superuser,
                    is_active,
                    num_items := count(.<owner[IS Item]),
                    items:= .<owner[IS Item] { id, title }
            }
            FILTER .email = <str>$email""",
            email=email,
        )
    except NoDataError:
        return None
    except Exception as e:
        print(f"EXCEPTION: {e}")
    user = User.parse_raw(result)
    return user


async def get_multi(
    con: AsyncIOConnection, *, skip: int = 0, limit: int = 100
) -> PaginatedUsers:
    try:
        result = await con.fetchone_json(
            """SELECT <json>(
                count:= count(User),
                data := array_agg(
                    User {
                        id,
                        full_name,
                        email,
                        is_superuser,
                        is_active,
                        num_items := count(.<owner[IS Item]),
                        items:= .<owner[IS Item] { id, title }
                    }
                )[<int16>$offset:<int16>$offset+<int16>$limit]
            )""",
            offset=skip,
            limit=limit,
        )
    except Exception as e:
        print(f"EXCEPTION: {e}")
    paginated_users = PaginatedUsers.parse_raw(result)
    return paginated_users


async def create(con: AsyncIOConnection, *, obj_in: UserCreate) -> User:
    try:
        result = await con.fetchone_json(
            """SELECT (
                INSERT User {
                    full_name := <str>$full_name,
                    email := <str>$email,
                    hashed_password := <str>$hashed_password,
                    is_superuser := <bool>$is_superuser,
                    is_active := <bool>$is_active
                }
            ) {
                id,
                full_name,
                email,
                is_superuser,
                is_active,
                num_items := count(.<owner[IS Item]),
                items:= .<owner[IS Item] { id, title }
            }""",
            full_name=obj_in.full_name,
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            is_superuser=obj_in.is_superuser,
            is_active=obj_in.is_active,
        )
    except Exception as e:
        print(f"EXCEPTION: {e}")
    user = User.parse_raw(result)
    return user


async def update(con: AsyncIOConnection, *, db_obj: User, obj_in: UserUpdate) -> User:
    update_data = obj_in.dict(exclude_unset=True)
    if update_data.get("password"):
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    shape = ", ".join([k + db.type_cast(update_data[k]) + k for k in update_data])
    try:
        result = await con.fetchone_json(
            f"""SELECT (
                UPDATE User
                FILTER .id = <uuid>$id
                SET {{ {shape} }}
            ) {{
                id,
                full_name,
                email,
                is_superuser,
                is_active,
                num_items := count(.<owner[IS Item]),
                items:= .<owner[IS Item] {{ id, title }}
            }}""",
            id=db_obj.id,
            **update_data,
        )
    except Exception as e:
        print(f"EXCEPTION: {e}")
    user = User.parse_raw(result)
    return user


async def authenticate(
    con: AsyncIOConnection, *, email: str, password: str
) -> Optional[UserInDB]:
    try:
        result = await con.fetchone_json(
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
        print(f"EXCEPTION: {e}")
    user = UserInDB.parse_raw(result)
    if not verify_password(password, user.hashed_password):
        return None
    return user
