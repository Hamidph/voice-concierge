# src/voice_concierge/utils/security.py
from typing import Union
from cryptography.fernet import Fernet
import base64
import hashlib

from voice_concierge.config import settings
from voice_concierge.utils.logging_utils import get_logger

logger = get_logger(__name__)


def get_encryption_key() -> bytes:
    """Get the encryption key, deriving it from settings if necessary."""
    if settings.encrypt_key:
        # If key is provided, use it
        key = settings.encrypt_key

        # Ensure the key is valid for Fernet (32 bytes base64-encoded)
        if len(key) < 32:
            # If key is too short, derive a key using the provided key as a password
            derived_key = hashlib.sha256(key.encode()).digest()
            key = base64.urlsafe_b64encode(derived_key)
        elif not key.endswith("="):
            # Ensure key is properly padded
            key = base64.urlsafe_b64encode(
                base64.urlsafe_b64decode(key + "=" * (-len(key) % 4))
            )
    else:
        # Generate a new key if none is provided
        key = Fernet.generate_key()
        logger.warning("No encryption key provided. Generated a new key.")

    return key


def encrypt_data(data: Union[str, bytes]) -> bytes:
    """Encrypt data using Fernet symmetric encryption.

    Args:
        data: String or bytes to encrypt

    Returns:
        Encrypted bytes
    """
    if not settings.encrypt_transcripts:
        if isinstance(data, str):
            return data.encode()
        return data

    key = get_encryption_key()
    f = Fernet(key)

    if isinstance(data, str):
        data = data.encode()

    return f.encrypt(data)


def decrypt_data(data: bytes) -> bytes:
    """Decrypt data using Fernet symmetric encryption.

    Args:
        data: Encrypted bytes

    Returns:
        Decrypted bytes
    """
    if not settings.encrypt_transcripts:
        return data

    key = get_encryption_key()
    f = Fernet(key)

    return f.decrypt(data)


def encrypt_file(input_path: str, output_path: str) -> str:
    """Encrypt a file.

    Args:
        input_path: Path to the file to encrypt
        output_path: Path to save the encrypted file

    Returns:
        Path to the encrypted file
    """
    if not settings.encrypt_transcripts:
        # If encryption is disabled, just copy the file
        if input_path != output_path:
            with open(input_path, "rb") as src, open(output_path, "wb") as dst:
                dst.write(src.read())
        return output_path

    with open(input_path, "rb") as f:
        data = f.read()

    encrypted_data = encrypt_data(data)

    with open(output_path, "wb") as f:
        f.write(encrypted_data)

    return output_path


def decrypt_file(input_path: str, output_path: str) -> str:
    """Decrypt a file.

    Args:
        input_path: Path to the encrypted file
        output_path: Path to save the decrypted file

    Returns:
        Path to the decrypted file
    """
    if not settings.encrypt_transcripts:
        # If encryption is disabled, just copy the file
        if input_path != output_path:
            with open(input_path, "rb") as src, open(output_path, "wb") as dst:
                dst.write(src.read())
        return output_path

    with open(input_path, "rb") as f:
        data = f.read()

    decrypted_data = decrypt_data(data)

    with open(output_path, "wb") as f:
        f.write(decrypted_data)

    return output_path
