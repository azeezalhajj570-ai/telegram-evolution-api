import base64
import os
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _get_key(key_bytes: Optional[bytes] = None) -> bytes:
    from app.config import settings

    raw = key_bytes or settings.encryption_key.encode()
    if len(raw) < 32:
        raw = raw.ljust(32, b"\0")
    return raw[:32]


def encrypt(plaintext: str, key_bytes: Optional[bytes] = None) -> str:
    key = _get_key(key_bytes)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    return base64.b64encode(nonce + ciphertext).decode()


def decrypt(ciphertext_b64: str, key_bytes: Optional[bytes] = None) -> str:
    key = _get_key(key_bytes)
    aesgcm = AESGCM(key)
    raw = base64.b64decode(ciphertext_b64)
    nonce, ciphertext = raw[:12], raw[12:]
    return aesgcm.decrypt(nonce, ciphertext, None).decode()
