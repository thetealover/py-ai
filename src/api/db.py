import logging
from contextlib import asynccontextmanager
from typing import List, Dict, Any
from psycopg_pool import AsyncConnectionPool
from src.config.settings import settings

logger = logging.getLogger(__name__)

db_pool: AsyncConnectionPool = None


async def get_db_pool() -> AsyncConnectionPool:
    """
    Returns a singleton instance of the AsyncConnectionPool for direct queries.
    Initializes the pool on the first call.
    """
    global db_pool
    if db_pool is None:
        logger.info("Initializing database connection pool for direct queries...")
        db_pool = AsyncConnectionPool(conninfo=settings.db_dsn, open=False)
        await db_pool.open(wait=True)
    return db_pool


@asynccontextmanager
async def get_db_connection():
    """Provides a managed database connection from the pool."""
    pool = await get_db_pool()
    async with pool.connection() as conn:
        yield conn


async def check_conversation_title_exists(thread_id: str) -> bool:
    """Checks if a title already exists for a given thread_id."""
    query = "select 1 from public.conversation_metadata where thread_id = %(thread_id)s;"
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, {"thread_id": thread_id})
            return await cur.fetchone() is not None


async def save_conversation_title(thread_id: str, title: str):
    """Saves or updates a conversation title in the metadata table."""
    query = """
            insert into public.conversation_metadata (thread_id, title)
            values (%(thread_id)s, %(title)s)
            on conflict (thread_id) do update set title      = excluded.title,
                                                  updated_at = now(); \
            """
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, {"thread_id": thread_id, "title": title})


async def get_conversations_for_user(username: str) -> List[Dict[str, Any]]:
    """
    Fetches all conversation threads for a given username, prioritizing AI-generated titles.
    """
    pattern = f"{username}-%"

    query = """
            with latest_checkpoints as (select thread_id,
                                               max(checkpoint_id) as max_checkpoint_id
                                        from checkpoints
                                        where thread_id like %(pattern)s
                                        group by thread_id),
                 first_checkpoints as (select distinct on (thread_id) thread_id,
                                                                      checkpoint -> 'channel_values' -> 'messages' -> 0 ->> 'content' as title
                                       from checkpoints
                                       where thread_id like %(pattern)s
                                         and jsonb_array_length(checkpoint -> 'channel_values' -> 'messages') > 0
                                       order by thread_id, checkpoint_id)
            select lc.thread_id,
                   coalesce(
                           meta.title,
                           fc.title,
                           'new chat'
                   ) as title
            from latest_checkpoints lc
                     left join public.conversation_metadata meta on lc.thread_id = meta.thread_id
                     left join first_checkpoints fc on lc.thread_id = fc.thread_id
            order by lc.max_checkpoint_id desc; \
            """

    conversations = []
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, {"pattern": pattern})
                results = await cur.fetchall()
                for row in results:
                    conversations.append({"conversation_id": row[0], "title": row[1]})
    except Exception as e:
        logger.error(f"Database error in get_conversations_for_user for '{username}': {e}")
        raise

    return conversations
