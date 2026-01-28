import asyncio
import re

from bs4 import BeautifulSoup

from .base import BaseScraper
from src.model import Car
from src.logger import logger


class CarScraper(BaseScraper):
    async def get_car_data(self, url: str, semaphore: asyncio.Semaphore) -> Car:
        async with semaphore:
            html = await self.fetch(url)
            soup = BeautifulSoup(html, "html.parser")

            def get_safe_text(selector: str) -> str | None:
                el = soup.select_one(selector)
                return el.get_text(strip=True) if el else None

            img_el = soup.select_one("span.picture img")
            image_url = ""
            if img_el:
                image_url = img_el.get("data-src")

            phone_number = await self.get_phone_number(soup)

            data = dict(
                url=url,
                title=get_safe_text("#basicInfoTitle h1"),
                price_usd=get_safe_text("#basicInfoPrice strong"),
                odometer=get_safe_text("#basicInfoTableMainInfo0 span"),
                username=get_safe_text("#sellerInfoUserName span"),
                image_url=image_url,
                image_count=int(soup.select_one("span.common-badge span:last-child").text),
                car_number=get_safe_text("div.car-number span"),
                car_vin=get_safe_text("#badgesVin span.common-text"),
                phone_number=phone_number,
            )
            car = Car(**data)
            logger.debug(f"Successfully parsed car: {url}")
            return car

    async def get_phone_number(self, soup: BeautifulSoup) -> str | None:
        payload = self._extract_phone_data(soup)
        if not payload:
            return None

        url = "https://auto.ria.com/bff/final-page/public/auto/popUp/"
        async with self.session.post(url, json=payload) as resp:
            resp.raise_for_status()
            data = await resp.json()

            if "additionalParams" in data and "phoneStr" in data["additionalParams"]:
                return data["additionalParams"]["phoneStr"]

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
