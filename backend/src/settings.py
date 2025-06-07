import os

from pydantic import RedisDsn, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


__all__ = ['settings', 'get_settings', 'Settings']


class Db(BaseModel):
    """
    Настройки для подключения к базе данных.
    """

    host: str
    port: int
    user: str
    password: str
    name: str
    scheme: str

    provider: str = 'postgresql+asyncpg'

    @property
    def dsn(self) -> str:
        return f'{self.provider}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}'
    
class Settings(BaseSettings):
    debug: bool
    base_url: str
    secret_key: str
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    cors_origins: list[str]


    db: Db

    redis_dsn: RedisDsn
    jwt_secret: str
    jwt_algorithm: str
    jwt_expire_hours: int

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_nested_delimiter='__',
        case_sensitive=False,
        extra='ignore',
    )

def get_settings():
    return Settings() # type: ignore

settings = get_settings()
