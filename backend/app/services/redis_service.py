import json
from typing import Any, Optional
from redis.asyncio import Redis, from_url
from app.config.settings import settings
from app.logging.config import logger

class RedisService:
    def __init__(self) -> None:
        self.client: Optional[Redis] = None

    def connect(self) -> None:
        if self.client is not None:
            return
        try:
            self.client = from_url(settings.REDIS_URL, decode_responses=True)
            logger.info("redis_connected_successfully", url=settings.REDIS_URL)
        except Exception as e:
            logger.critical("redis_connection_failed", url=settings.REDIS_URL, error=str(e))
            raise e

    async def disconnect(self) -> None:
        if self.client is not None:
            await self.client.close()
            self.client = None
            logger.info("redis_disconnected_successfully")

    async def _get_client(self) -> Redis:
        if self.client is None:
            self.connect()
        return self.client

    async def get(self, key: str) -> Optional[str]:
        client = await self._get_client()
        return await client.get(key)

    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        client = await self._get_client()
        return await client.set(name=key, value=value, ex=expire)

    async def get_json(self, key: str) -> Optional[Any]:
        val = await self.get(key)
        if val:
            try:
                return json.loads(val)
            except Exception:
                return None
        return None

    async def set_json(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        return await self.set(key, json.dumps(value), expire=expire)

    async def delete(self, key: str) -> int:
        client = await self._get_client()
        return await client.delete(key)

    async def exists(self, key: str) -> bool:
        client = await self._get_client()
        return await client.exists(key) > 0

    async def incr(self, key: str, amount: int = 1) -> int:
        client = await self._get_client()
        return await client.incr(key, amount)

    async def expire(self, key: str, time: int) -> bool:
        client = await self._get_client()
        return await client.expire(key, time)

    async def ttl(self, key: str) -> int:
        client = await self._get_client()
        return await client.ttl(key)

    async def ping(self) -> bool:
        try:
            client = await self._get_client()
            return await client.ping()
        except Exception as e:
            logger.error("redis_ping_failed", error=str(e))
            return False

redis_service = RedisService()
