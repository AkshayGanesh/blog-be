from pydantic import BaseSettings


class Configurations(BaseSettings):
    thumbnail_directory: str

    logger_level: str
    logger_format: str

    permanent_token: str
    encryption_key: str
    refresh_token_duration: int

    api_prefix: str

    class Config:
        """Config."""

        env_prefix = ""
        env_file = ".env"
        env_file_encoding = "utf-8"


config = Configurations()