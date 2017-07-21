from config import DATABASE
import asyncio
import asyncpg


class Database:

    _connection : asyncpg.Connection = None

    def _set_connection(self, con):
        Database._connection = con

    @staticmethod
    async def get_connection() -> asyncpg.Connection:
        if not Database._connection or Database._connection.is_closed():
            Database()._set_connection(await asyncpg.connect(**DATABASE))
        return Database._connection

# have to use commit() on connection
