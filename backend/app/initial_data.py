import asyncio
import logging
from pathlib import Path
from typing import Optional

from edgedb import AsyncIOConnection, async_connect

from app import crud, schemas
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


async def check_db() -> Optional[AsyncIOConnection]:
    for attempt in range(max_tries):
        try:
            con = await async_connect(
                host=settings.EDGEDB_HOST,
                database=settings.EDGEDB_DB,
                user=settings.EDGEDB_USER,
            )
            # Try to create session to check if DB is awake
            await con.execute("SELECT 1")
            return con
        except Exception as e:
            if attempt < max_tries - 1:
                logger.error(
                    f"""{e}
Attempt {attempt + 1}/{max_tries} to connect to database, waiting {wait_seconds}s."""
                )
                await asyncio.sleep(wait_seconds)
            else:
                raise e
    return None


async def init_db(con: AsyncIOConnection) -> None:
    with open(Path("./dbschema/database.esdl")) as f:
        schema = f.read()
    async with con.transaction():
        await con.execute(f"""START MIGRATION TO {{ {schema} }}""")
        await con.execute("""POPULATE MIGRATION""")
        await con.execute("""COMMIT MIGRATION""")
    user = await crud.user.get_by_email(con, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        await crud.user.create(con, obj_in=user_in)


async def main() -> None:
    logger.info("Initializing service")
    con = await check_db()
    logger.info("Service finished initializing")
    if con:
        logger.info("Creating initial data")
        await init_db(con)
        logger.info("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
