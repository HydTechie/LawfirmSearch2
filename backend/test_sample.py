import hashlib

def encrypt_password(password: str) -> str:
    """Encrypts a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()