# src/voice_concierge/utils/file_utils.py
import os
import tempfile

from voice_concierge.utils.logging_utils import get_logger

logger = get_logger(__name__)


def ensure_directory(directory: str) -> str:
    """Ensure that a directory exists, creating it if necessary.

    Args:
        directory: Directory path

    Returns:
        The absolute path to the directory
    """
    directory = os.path.abspath(directory)
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")
    return directory


def get_temp_file(suffix: str = None) -> str:
    """Get a temporary file path.

    Args:
        suffix: Optional file suffix (e.g., '.mp3')

    Returns:
        Path to a temporary file
    """
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    return path


def save_binary_data(data: bytes, file_path: str) -> str:
    """Save binary data to a file.

    Args:
        data: Binary data to save
        file_path: Path to save the data to

    Returns:
        The absolute path to the saved file
    """
    directory = os.path.dirname(file_path)
    if directory:
        ensure_directory(directory)

    with open(file_path, "wb") as f:
        f.write(data)

    return os.path.abspath(file_path)
