# GCM STUFF: https://www.pycryptodome.org/src/cipher/modern#gcm-mode

import hashlib
import hmac
import json
from base64 import b64encode
from typing import Union

from Crypto.Cipher import AES


def fingerprint_sha256(data: Union[bytes, str]) -> str:
    """Generate a SHA-256 fingerprint.

    Args:
        data: Raw key material to hash. Accepts ``bytes`` or ``str`` (UTF-8
            encoded before hashing).

    Returns:
        Hex-encoded SHA-256 digest (64 characters).
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def constant_time_equals(a: Union[bytes, str], b: Union[bytes, str]) -> bool:
    """Compare two values in constant time.

    Args:
        a: First value (digest or plain data), ``bytes`` or ``str``.
        b: Second value, same rules as ``a``.

    Returns:
        ``True`` if the values are identical, otherwise ``False``.
    """
    if isinstance(a, str):
        a = a.encode("utf-8")
    if isinstance(b, str):
        b = b.encode("utf-8")
    return hmac.compare_digest(a, b)


def aes_gcm_encrypt(
    data: bytes,
    key: bytes,
    header: bytes = b"header",
) -> str:
    """Encrypts data using AES-GCM mode with optional header and key.

    Args:
        data: The data to encrypt
        key: Encryption key
        header: Additional authenticated data (default: b"header")

    Returns:
        JSON string containing nonce, header, ciphertext, and authentication tag
    """
    # if key is None:
    #     key = get_random_bytes(16)

    cipher = AES.new(key, AES.MODE_GCM)
    cipher.update(header)

    ciphertext, tag = cipher.encrypt_and_digest(data)

    json_k = ["nonce", "header", "ciphertext", "tag"]
    json_v = [
        b64encode(x).decode("utf-8") for x in (cipher.nonce, header, ciphertext, tag)
    ]
    result = json.dumps(dict(zip(json_k, json_v)))
    return result


# Example usage:
# aes_gcm_encrypt(b"secret")
