import asyncio

from bs4 import BeautifulSoup

from .base import BaseScraper
from src.logger import logger


class PageScraper(BaseScraper):
    async def get_links_from_page(
        self, page: int, semaphore: asyncio.Semaphore
    ) -> list[str]:
        url = f"{self.base_url}?{page=}"
        async with semaphore:
            html = await self.fetch(url)
            soup = BeautifulSoup(html, "html.parser")
            links = []
            for a in soup.select("a.address"):
                link = a.get("href")
                if "newauto" in link:
                    continue
                links.append(link)

        logger.info(f"Links collected from page {page}: {len(links)}")
        return links

    async def get_links_from_pages(self, start: int, end: int) -> list[str]:
        semaphore = asyncio.Semaphore(20)
        tasks = [
            self.get_links_from_page(page, semaphore) for page in range(start, end)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_links = []
        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                logger.error(f"Page {i} failed with {result}")
            if isinstance(result, list):
                all_links.extend(result)

        logger.info(f"Links collected from pages in range: [{start}, {end}]")
        return all_links

    async def get_max_page(self) -> int:
        url = f"{self.base_url}?page=1"
        html = await self.fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        max_page = soup.select_one("span.page-item.dhide.text-c").text
        return int(max_page.replace(" ", "").split("/")[-1])
