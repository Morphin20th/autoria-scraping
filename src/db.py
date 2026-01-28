import os
import subprocess
from datetime import datetime

import psycopg

from src.logger import logger
from src.model import Car
from src.settings import settings


async def get_connection() -> psycopg.AsyncConnection:
    return await psycopg.AsyncConnection.connect(settings.database_url)


class DBRepository:
    def __init__(self, conn: psycopg.AsyncConnection):
        self.conn = conn

    async def insert_cars(self, cars: list[Car]) -> None:
        if not cars:
            return

        query = """
        INSERT INTO cars (
            url, title, price_usd, odometer, username, phone_number, 
            image_url, image_count, car_number, car_vin 
        ) VALUES (
            %(url)s, %(title)s, %(price_usd)s, %(odometer)s, %(username)s, %(phone_number)s, 
            %(image_url)s, %(image_count)s, %(car_number)s, %(car_vin)s
        )
        ON CONFLICT (url)
        DO NOTHING;
        """

        async with self.conn.cursor() as cursor:
            car_dicts = [car.model_dump() for car in cars]
            await cursor.executemany(query, car_dicts)
            await self.conn.commit()


async def make_db_dump(database_url: str) -> None:
    dump_dir = "/app/dumps"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"autoria_dump_{timestamp}.sql"
    full_path = os.path.join(dump_dir, filename)

    command = f"pg_dump {database_url} -f {full_path}"

    try:
        subprocess.run(command, shell=True, check=True)
        logger.info(f"Database dump successfully created: {filename}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create database dump: {e}")
