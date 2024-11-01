import logging
import sys
import os
from datetime import datetime

log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"


def setup_logging():
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.ERROR)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    loggers = {
        "github_service": logging.getLogger("github_service"),
        "openai_service": logging.getLogger("openai_service"),
        "repository_service": logging.getLogger("repository_service"),
        "cache_service": logging.getLogger("cache_service"),
    }

    for logger in loggers.values():
        logger.setLevel(logging.ERROR)

    return loggers


logger = setup_logging()
