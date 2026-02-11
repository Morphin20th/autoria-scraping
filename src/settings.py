from dotenv import load_dotenv
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env", env_file_encoding="utf-8", extra="ignore"
    )

    BASE_URL: str = "https://auto.ria.com/uk/car/used/"

    POSTGRES_DB: str = "autoria"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    @property
    def database_url(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql",
                path=self.POSTGRES_DB,
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                port=self.POSTGRES_PORT,
                host=self.POSTGRES_HOST,
            )
        )


settings = AppSettings()
