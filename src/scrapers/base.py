import asyncio

import aiohttp

from src.settings import settings

class BaseScraper:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.base_url = settings.BASE_URL

    async def fetch(self, url: str) -> str:
        try:
            await asyncio.sleep(0.2)
            async with self.session.get(url, timeout=20) as response:
                if response.status == 429:
                    print("Too many requests, waiting")
                    await asyncio.sleep(10)
                    return ""
                response.raise_for_status()
                content = await response.read()
                return content.decode("utf-8", errors="ignore")

        except Exception as e:
            print(f"Error occurred during {url}: {e}")
            return ""
