import logging
import logging.config
import os


class Settings:
    """Applicatieconfiguratie voor de Presidio-NL API.

    Bevat standaardwaarden voor debugmodus, ondersteunde entiteiten, taal,
    en de te gebruiken NLP-modellen (spaCy of transformers).
    """
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    DEFAULT_ENTITIES = [
        "PERSON",
        "LOCATION",
        "PHONE_NUMBER",
        "EMAIL",
        "ORGANIZATION",
        "IBAN",
        "ADDRESS",
    ]

    DEFAULT_LANGUAGE = "nl"
    DEFAULT_NLP_ENGINE = "spacy"
    DEFAULT_SPACY_MODEL = "nl_core_news_md"
    DEFAULT_TRANSFORMERS_MODEL = "pdelobelle/robbert-v2-dutch-base"


settings: Settings = Settings()


def setup_logging() -> None:
    """Configureer logging voor de applicatie.

    Stelt zowel een file- als streamhandler in, met DEBUG- of INFO-niveau
    afhankelijk van de configuratie. Logt naar 'app.log' en de console.
    """
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
