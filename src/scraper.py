import aiohttp
from bs4 import BeautifulSoup

from src.settings import settings

class CarScraper:
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.session = session
        self.base_url = settings.BASE_URL

    async def fetch(self, url: str) -> str:
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.text()

    async def get_links(self, url: str) -> list[str]:
        html = await self.fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        links = []
        for a in soup.select("a.address"):
            link = a.get("href")
            if "newauto" in link:
                continue
            links.append(a.get("href"))

        return links

    async def get_car_data(self, url: str) -> dict:
        html = await self.fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        def get_safe_text(selector: str) -> str:
            el = soup.select_one(selector)
            return el.get_text(strip=True) if el else ""

        img_el = soup.select_one("span.picture img")
        image_url = ""
        if img_el:
            image_url = img_el.get("data-src")

        data = dict(
            url=url,
            title=get_safe_text("#sideTitleTitle span"),
            price_usd=get_safe_text("#sidePrice strong"),
            odometer=get_safe_text("#basicInfoTableMainInfo0 span"),
            username=get_safe_text("#sellerInfoUserName span"),
            image_url=image_url,
            image_count = int(
                soup.select_one("span.common-badge span:last-child").text
            ),
            car_number=get_safe_text("div.car-number span"),
            car_vin=get_safe_text("#badgesVin span.common-text")
        )

        return data
