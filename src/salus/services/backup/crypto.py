import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return kdf.derive(password.encode())


def encrypt(data: bytes, password: str) -> bytes:
    """
    Encrypt data using AES-GCM-256 with key derived from password using PBKDF2.
    Format: Salt (16 bytes) | IV (12 bytes) | Ciphertext + Tag
    """
    salt = os.urandom(16)
    iv = os.urandom(12)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(iv, data, None)
    return salt + iv + ciphertext


def decrypt(data: bytes, password: str) -> bytes:
    """
    Decrypt data encrypted with the encrypt() function.
    """
    if len(data) < 16 + 12 + 16:
        raise ValueError("Ciphertext is too short or corrupted.")
    salt = data[:16]
    iv = data[16:28]
    ciphertext = data[28:]
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(iv, ciphertext, None)
