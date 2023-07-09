import sys

from loguru import logger

from src.common.settings import config


def configure_logger() -> None:
    """Configure logger."""
    logger.remove()
    logger.add(
        sys.stderr,
        format=config.logger_format,
        level=config.logger_level,
    )
