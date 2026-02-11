import psycopg

from src.db import DBRepository, make_db_dump
from src.logger import logger
from src.model import Car
from src.scrapers import PageScraper, CarScraper
from src.settings import settings


class Orchestrator:
    def __init__(
        self,
        page_scraper: PageScraper,
        car_scraper: CarScraper,
        db_repo: DBRepository,
        conn: psycopg.AsyncConnection,
    ) -> None:
        self.page_scraper = page_scraper
        self.car_scraper = car_scraper
        self.db_repo = db_repo
        self.conn = conn
        self.links_batch_size = 50

    async def _save_to_db(self, cars: list[Car]) -> None:
        try:
            async with self.conn.transaction():
                await self.db_repo.insert_cars(cars, self.conn)
        except psycopg.Error as e:
            logger.error(f"Database transaction failed: {e}")
            raise

    async def run_cycle(self):
        max_page = await self.page_scraper.get_max_page()
        if not max_page:
            logger.error("No max page found")
            return

        for i in range(1, max_page + 1, self.links_batch_size):
            current_batch_count = min(self.links_batch_size, max_page - i + 1)
            logger.info(
                f"--- Processing batch: pages {i} to {i + current_batch_count - 1} ---"
            )
            links = await self.page_scraper.get_links_from_pages(
                i, i + current_batch_count - 1
            )
            cars = await self.car_scraper.get_cars(links)
            await self._save_to_db(cars)

        await make_db_dump(settings.database_url)
