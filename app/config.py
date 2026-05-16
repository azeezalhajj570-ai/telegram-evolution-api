from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/telegram_gateway"
    redis_url: str = "redis://localhost:6379/0"
    encryption_key: str = ""
    api_keys: str = ""
    telegram_api_id: int = 0
    telegram_api_hash: str = ""
    webhook_retry_max: int = 3
    webhook_retry_base_delay: int = 60

    @property
    def api_keys_list(self) -> List[str]:
        return [k.strip() for k in self.api_keys.split(",") if k.strip()]


settings = Settings()
