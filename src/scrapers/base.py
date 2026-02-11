import asyncio

import aiohttp

from src.logger import logger
from src.settings import settings


class BaseScraper:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.base_url = settings.BASE_URL

    async def fetch(self, url: str) -> str:
        response = await self._request("GET", url)
        return response if response else ""

    async def post(self, url: str, payload: dict) -> dict | None:
        return await self._request("POST", url, json=payload)

    async def _request(
        self, method: str, url: str, retries: int = 3, **kwargs
    ) -> str | dict | None:
        for attempt in range(retries):
            try:
                await asyncio.sleep(0.5 * (attempt + 1))
                async with self.session.request(
                    method, url, timeout=20, **kwargs
                ) as response:
                    if response.status == 429:
                        wait_time = 15 * (attempt + 1)
                        logger.warning(f"429 Too Many Requests {url}")
                        await asyncio.sleep(wait_time)
                        continue

                    response.raise_for_status()

                    if "application/json" in response.headers.get("Content-Type"):
                        return await response.json()

                    return await response.text(errors="ignore")
            except Exception as e:
                logger.error(
                    f"Attempt {attempt + 1} for request {method} {url} failed: {e}"
                )
                if attempt == retries - 1:
                    return None
        return None
