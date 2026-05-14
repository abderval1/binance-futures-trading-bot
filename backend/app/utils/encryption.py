from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64
import os
from ..config import settings


def _derive_key(key_material: str, salt: bytes) -> bytes:
    """Derive 32-byte AES key from secret using SHA-256"""
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(key_material.encode())
    digest.update(salt)
    return digest.finalize()


def encrypt_api_key(api_key: str, secret_key: str) -> tuple[str, str]:
    """Encrypt API keys using AES-256-GCM. Returns (encrypted_api, nonce)"""
    salt = os.urandom(16)
    key = _derive_key(settings.encryption_key, salt)
    aesgcm = AESGCM(key)

    combined = f"{api_key}|||{secret_key}"
    nonce = os.urandom(12)
    encrypted = aesgcm.encrypt(nonce, combined.encode(), None)

    # Store salt+encrypted together (salt is needed for decryption)
    payload = salt + encrypted
    return base64.b64encode(payload).decode(), base64.b64encode(nonce).decode()


def decrypt_api_key(encrypted_data: str, nonce_b64: str) -> tuple[str, str]:
    """Decrypt stored API keys. Returns (api_key, secret_key)"""
    payload = base64.b64decode(encrypted_data)
    nonce = base64.b64decode(nonce_b64)

    salt = payload[:16]
    encrypted = payload[16:]

    key = _derive_key(settings.encryption_key, salt)
    aesgcm = AESGCM(key)

    decrypted = aesgcm.decrypt(nonce, encrypted, None).decode()
    api_key, secret_key = decrypted.split("|||")
    return api_key, secret_key
