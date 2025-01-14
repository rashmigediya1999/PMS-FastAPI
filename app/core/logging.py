import logging.config
from app.core.config import settings

class Logger:
    @staticmethod
    def setup_logging():
        logging.config.dictConfig(settings.config["logging"])

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)
