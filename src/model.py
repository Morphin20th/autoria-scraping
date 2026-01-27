from pydantic import BaseModel, field_validator


class Car(BaseModel):
    url: str
    title: str
    price_usd: int
    odometer: int
    username: str
    # phone_number: int
    image_url: str
    image_count: int
    car_number: str | None
    car_vin: str | None

    @field_validator("odometer", mode="before")
    @classmethod
    def parse_odometer(cls, value: str) -> int:
        num = int(value.split()[0])
        return num * 1000

    # @field_validator("phone_number", mode="before")
    # @classmethod
    # def parse_phone_number(cls, value: str) -> int:
    #     value = value.replace("(", "").replace(")", "").replace(" ", "")
    #     value = "38" + value
    #     return int(value)

    @field_validator("price_usd", mode="before")
    @classmethod
    def parse_price_usd(cls, value: str) -> int:
        value = value.replace(" ", "").replace("$", "").replace("\xa0", "")
        return int(value)
