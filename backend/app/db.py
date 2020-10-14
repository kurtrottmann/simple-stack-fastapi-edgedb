from typing import AsyncGenerator

from edgedb import AsyncIOConnection, AsyncIOPool, create_async_pool

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
