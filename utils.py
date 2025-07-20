import json
import hashlib
from cryptography.fernet import Fernet
import base64

# Generate key only ONCE and keep it safe
def generate_key(password: str) -> bytes:
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

# Encrypt a file
def encrypt_file(data: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(data)

# Decrypt a file
def decrypt_file(data: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(data)

# Compute SHA-256 hash of data
def compute_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def hash_dict(d: dict) -> str:
    """Deterministic hash of dictionary."""
    block_string = json.dumps(d, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()
