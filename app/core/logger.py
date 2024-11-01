import logging
import sys
from app.core.config import settings

def setup_logging():
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log')
        ]
    )

    loggers = {
        'github_service': logging.getLogger('github_service'),
        'openai_service': logging.getLogger('openai_service'),
        'repository_service': logging.getLogger('repository_service'),
        'file_service': logging.getLogger('file_service'),
        'cache_service': logging.getLogger('cache_service'),
    }

    for logger in loggers.values():
        logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    return loggers

logger = setup_logging()
