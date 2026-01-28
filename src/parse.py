import asyncio

import aiohttp

from src.db import get_connection, DBRepository, make_db_dump
from src.logger import logger
from src.model import Car
from src.scrapers import PageScraper, CarScraper
from src.settings import settings


async def main():
    connector = aiohttp.TCPConnector(limit=5)
    async with aiohttp.ClientSession(connector=connector) as session:
        page_scraper = PageScraper(session)
        links = await page_scraper.get_links()
        logger.info(f"Links were found {len(links)}")

        car_scraper = CarScraper(session)
        semaphore = asyncio.Semaphore(5)

        tasks = [car_scraper.get_car_data(link, semaphore) for link in links]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        cars = [res for res in results if isinstance(res, Car)]
        logger.info(f"Cars: {len(cars)}")

    conn = await get_connection()
    try:
        async with conn:
            db = DBRepository(conn)
            await db.insert_cars(cars)
    except Exception as e:
        logger.error(f"Database error: {e}")

    await make_db_dump(settings.database_url)


async def orchestrator():
    while True:
        try:
            logger.info("--- Starting new scraping session ---")
            await main()
            logger.info("Session finished successfully.")
        except Exception as e:
            logger.error(f"Critical error in orchestrator: {e}")

        logger.info("Waiting 12 hours until next run")
        await asyncio.sleep(12 * 3600)


if __name__ == "__main__":
    asyncio.run(orchestrator())
