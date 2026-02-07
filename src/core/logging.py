import logging
import os
from logging.handlers import TimedRotatingFileHandler

from src.core.config import settings


class TextFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
    }
    RESET = "\033[0m"

    def __init__(self, fmt: str, use_color: bool) -> None:
        super().__init__(fmt=fmt)
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        original_levelname = record.levelname
        if self.use_color and record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
            )
        formatted = super().format(record)
        record.levelname = original_levelname
        return formatted


def setup_logging() -> None:
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    log_format = "[%(asctime)s] [%(levelname)s] %(name)s %(message)s"

    handlers: list[logging.Handler] = []

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(
        TextFormatter(log_format, use_color=settings.log_color)
    )
    handlers.append(console_handler)

    if settings.log_dir:
        os.makedirs(settings.log_dir, exist_ok=True)
        log_path = os.path.join(settings.log_dir, settings.log_file)
        file_handler = TimedRotatingFileHandler(
            log_path,
            when=settings.log_rotation_when,
            backupCount=settings.log_backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(TextFormatter(log_format, use_color=False))
        handlers.append(file_handler)

    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)
