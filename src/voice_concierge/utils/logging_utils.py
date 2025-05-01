# src/voice_concierge/utils/logging_utils.py
import logging
import os
import sys

from voice_concierge.config import settings

# Ensure log directory exists
log_dir = os.path.dirname(settings.log_file)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configure root logger
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler(sys.stdout),
    ],
)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.

    Args:
        name: Name for the logger, typically __name__

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    return logger
