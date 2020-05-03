from pathlib import Path
from typing import Any, AsyncGenerator

from edgedb import AsyncIOConnection, AsyncIOPool, async_connect, create_async_pool

from . import crud, schemas
from .config import settings

pool: AsyncIOPool


async def create_pool() -> None:
    global pool
    pool = await create_async_pool(
        host=settings.EDGEDB_HOST,
        database=settings.EDGEDB_DB,
        user=settings.EDGEDB_USER,
    )


async def close_pool() -> None:
    await pool.aclose()


async def get_con() -> AsyncGenerator[AsyncIOConnection, None]:
    try:
        con = await pool.acquire()
        yield con
    finally:
        await pool.release(con)


def type_cast(value: Any) -> str:
    if type(value) == bool:
        return " := <bool>$"
    elif type(value) == str:
        return " := <str>$"
    else:
        raise ValueError("Type cast not found.")


async def init_db() -> None:
    con = await async_connect(
        host=settings.EDGEDB_HOST,
        database=settings.EDGEDB_DB,
        user=settings.EDGEDB_USER,
    )
    with open(Path("database.esdl")) as f:
        schema = f.read()
    async with con.transaction():
        await con.execute(f"""CREATE MIGRATION initdb TO {{ {schema} }}""")
        await con.execute(f"""COMMIT MIGRATION initdb""")
    user = await crud.user.get_by_email(con, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        await crud.user.create(con, obj_in=user_in)
