from pydantic import BaseModel, field_validator

from src.logger import logger


class Car(BaseModel):
    url: str
    title: str | None = None
    price_usd: int = 0
    odometer: int = 0
    username: str | None = None
    phone_number: str | None = None
    image_url: str | None = None
    image_count: int = 0
    car_number: str | None = None
    car_vin: str | None = None

    @field_validator("odometer", mode="before")
    @classmethod
    def parse_odometer(cls, value: str) -> int:
        if not value:
            logger.warning("Failed to extract odometer")
            return 0
        num = value.split()[0]
        return 0 if num.lower() == "без" else int(num) * 1000

    @field_validator("phone_number", mode="before")
    @classmethod
    def parse_phone_number(cls, value: str | None) -> str | None:
        if not value:
            logger.warning("Failed to extract phone number")
            return None
        value = value.replace("(", "").replace(")", "").replace(" ", "")
        value = "38" + value
        return value

    @field_validator("price_usd", mode="before")
    @classmethod
    def parse_price_usd(cls, value: str) -> int:
        if not value:
            logger.warning("Failed to extract price_usd")
            return 0
        try:
            clean_value = "".join(filter(str.isdigit, value))
            return int(clean_value) if clean_value else 0
        except ValueError:
            return 0
