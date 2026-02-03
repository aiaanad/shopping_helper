import aiohttp
import asyncio
from typing import Dict, Optional, Any
import json
import logging

logger = logging.getLogger(__name__)


class AsyncHttpClient:
    def __init__(self, max_concurrent: int = 10):
        self.session = None
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self._cache: Dict[str, str] = {}

    async def get(self, url: str, params: Optional[Dict] = None) -> Optional[str]:
        cache_key = f'{url}_{json.dumps(params, sort_keys=True) if params else ""}'

        if cache_key in self._cache:
            return self._cache[cache_key]

        async with self.semaphore:
            try:
                if not self.session:
                    self.session = aiohttp.ClientSession()

                async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response.raise_for_status()
                    content = await response.text()
                    self._cache[cache_key] = content
                    return content
            except Exception as e:
                logger.error(f"Async HTTP error: {e}")
                return None

    async def close(self):
        if self.session:
            await self.session.close()

    def clear_cache(self):
        self._cache.clear()