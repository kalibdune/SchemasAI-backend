import os
import time
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings as _BaseSettings
from pydantic_settings import SettingsConfigDict

os.environ["TZ"] = "UTC"
time.tzset()


class BaseConfig(_BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )


class APPConfig(BaseConfig, env_prefix="APP_"):
    encrypt_type: Literal["argon2"]
    hash_algorithm: str
    secret_key: str
    access_token_expire: int
    refresh_token_expire: int


class PostgresConfig(BaseConfig, env_prefix="DB_"):
    host: str
    user: str
    password: SecretStr
    name: str
    port: int
    debug: bool

    @property
    def get_dsn(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}"

    @property
    def get_dsn_psycopg(self) -> str:
        return f"postgresql+psycopg://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}"


class RabbitConfig(BaseConfig, env_prefix="RABBIT_"):
    host: str
    user: str
    password: SecretStr
    port: int

    @property
    def get_url(self) -> str:
        return f"amqp://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/"


class Config(BaseConfig):
    app: APPConfig
    postgres: PostgresConfig
    rabbit: RabbitConfig


config = Config(postgres=PostgresConfig(), app=APPConfig(), rabbit=RabbitConfig())
