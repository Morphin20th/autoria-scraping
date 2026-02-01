import asyncio

import aiohttp

from src.db import get_connection, DBRepository
from src.logger import logger
from src.orchestrator import Orchestrator
from src.scrapers import CarScraper, PageScraper


async def main():
    while True:
        try:
            logger.info("--- Starting new scraping session ---")
            connector = aiohttp.TCPConnector(limit=10)
            async with aiohttp.ClientSession(connector=connector) as session:
                page_scraper = PageScraper(session)
                car_scraper = CarScraper(session)
                db_repo = DBRepository()
                conn = await get_connection()
                async with conn:
                    orchestrator = Orchestrator(
                        page_scraper, car_scraper, db_repo, conn
                    )
                    await orchestrator.run_cycle()
            logger.info("Session finished successfully.")
        except Exception as e:
            logger.error(f"Critical error in orchestrator: {e}")
        logger.info("Waiting 12 hours until next run")
        await asyncio.sleep(12 * 3600)


if __name__ == "__main__":
    asyncio.run(main())
