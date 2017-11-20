from config import DATABASE
import asyncio
import asyncpg


class Database:

    _pool = None

    def _set_pool(self, pool):
        Database._pool = pool

    @staticmethod
    async def get_connection(loop) -> asyncpg.Connection:
        if not Database._pool:
            Database()._set_pool(await asyncpg.create_pool(loop=loop, **DATABASE))
        return await Database._pool.acquire()

    @staticmethod
    async def init_connection(loop):
        if not Database._pool:
            Database()._set_pool(await asyncpg.create_pool(loop=loop, max_size=50, **DATABASE))

    @staticmethod
    async def close_connection(con):
        await Database._pool.release(con)



# have to use commit() on connection
