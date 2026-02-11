import asyncio
import re

from bs4 import BeautifulSoup

from .base import BaseScraper
from src.model import Car
from src.logger import logger


class CarScraper(BaseScraper):
    async def get_cars(self, links: list) -> list[Car]:
        semaphore = asyncio.Semaphore(15)
        tasks = [self.get_car_data(link, semaphore) for link in links]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        cars = [res for res in results if isinstance(res, Car)]
        logger.info(f"Cars collected: {len(cars)}")

        return cars

    async def get_car_data(self, url: str, semaphore: asyncio.Semaphore) -> Car | None:
        async with semaphore:

            def get_by_selector(selector: str) -> str | None:
                nonlocal current_field
                try:
                    el = soup.select_one(selector)
                    return el.get_text(strip=True) if el else None
                except Exception as er:
                    logger.error(
                        f"Error occurred during selecting {selector} "
                        f"working with field {current_field}: {er}"
                    )
                    return None

            html = await self.fetch(url)
            if not html:
                logger.error(f"Skipping {url} due to empty response")
                return None

            soup = BeautifulSoup(html, "html.parser")
            data = dict()

            if soup.select_one("div.selled-auto"):
                logger.debug(f"Auto {url} is sold")
                return None

            data["url"] = url
            try:
                current_field = "title"
                data[current_field] = get_by_selector("#basicInfoTitle h1")

                current_field = "price_usd"
                data[current_field] = get_by_selector("#basicInfoPrice strong")

                current_field = "odometer"
                data[current_field] = get_by_selector("#basicInfoTableMainInfo0 span")

                current_field = "username"
                data[current_field] = get_by_selector("#sellerInfoUserName span")

                current_field = "image_url"
                img_el = soup.select_one("span.picture img")
                if img_el:
                    data[current_field] = img_el.get("data-src", None)

                current_field = "image_count"
                data[current_field] = get_by_selector(
                    "span.common-badge span:last-child"
                )

                current_field = "car_number"
                data[current_field] = get_by_selector("div.car-number span")

                current_field = "car_vin"
                data[current_field] = get_by_selector("#badgesVin span.common-text")

                current_field = "phone_number"
                data[current_field] = await self.get_phone_number(soup)

                car = Car(**data)
                logger.debug(f"Successfully parsed car: {url}")
            except Exception as e:
                logger.error(f"Failed to parse car {url}: {e}")
                return None
            return car

    async def get_phone_number(self, soup: BeautifulSoup) -> str | None:
        try:
            await asyncio.sleep(2)
            payload = self._extract_phone_data(soup)
            if not payload:
                return None

            url = "https://auto.ria.com/bff/final-page/public/auto/popUp/"

            resp = await self.post(url, payload)
            if "additionalParams" in resp and "phoneStr" in resp["additionalParams"]:
                return resp["additionalParams"]["phoneStr"]
            return None

        except Exception as e:
            logger.error(f"Failed to fetch phone number: {e}")
            return None

    @staticmethod
    def _extract_phone_data(soup: BeautifulSoup) -> dict | None:
        scripts = soup.find_all("script")

        for script in scripts:
            if script.string:
                auto_id_match = re.search(r'"autoId["\']?\s*:\s*(\d+)', script.string)
                user_id_match = re.search(
                    r'"userId["\']?\s*:\s*["\']?(\d+)', script.string
                )
                phone_id_match = re.search(
                    r'"phoneId["\']?\s*:\s*["\']?(\d+)', script.string
                )

                if auto_id_match and user_id_match and phone_id_match:
                    return {
                        "popUpId": "autoPhone",
                        "autoId": int(auto_id_match.group(1)),
                        "data": [
                            ["userId", user_id_match.group(1)],
                            ["phoneId", phone_id_match.group(1)],
                        ],
                    }
        return None
