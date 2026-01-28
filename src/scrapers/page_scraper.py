import asyncio

from bs4 import BeautifulSoup

from .base import BaseScraper
from src.logger import logger


class PageScraper(BaseScraper):
    async def get_links_from_page(self, page: int, semaphore: asyncio.Semaphore) -> list[str]:
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

    async def get_links(self) -> list[str]:
        max_page = await self.get_max_page()
        semaphore = asyncio.Semaphore(5)

        tasks = [self.get_links_from_page(page, semaphore) for page in range(1, 50)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        all_links = [link for page_links in results for link in page_links]

        logger.info(f"Links collected from all pages: {len(all_links)}")
        return all_links

    async def get_max_page(self):
        url = f"{self.base_url}?page=1"
        html = await self.fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        max_page = soup.select_one("span.page-item.dhide.text-c").text
        return int(max_page.replace(" ","").split("/")[-1])
