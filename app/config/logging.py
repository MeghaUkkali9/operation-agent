import logging
import sys

from pythonjsonlogger.json import JsonFormatter

from app.config.settings import get_settings


def configure_logging() -> None:
    settings = get_settings()

    handler = logging.StreamHandler(sys.stdout)
    formatter = JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(settings.log_level)

    # avoid double-logging requests we already log via middleware
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
