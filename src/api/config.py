import logging
import logging.config
import os


class Settings:
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"


settings: Settings = Settings()


def setup_logging() -> None:
    """Configureer logging."""
    console_log_level = "DEBUG" if settings.DEBUG else "INFO"
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "file": {
                    "class": "logging.FileHandler",
                    "formatter": "default",
                    "level": "DEBUG",
                    "filename": "app.log",
                },
                "stream": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": console_log_level,
                },
            },
            "root": {
                "level": "DEBUG",
                "handlers": ["file", "stream"],
            },
            "loggers": {
                # "add custom loggers to disable here!"
            },
        }
    )

    logging.debug("Logging is configured.")
