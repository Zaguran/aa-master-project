import hashlib
import secrets


def hash_password(password: str) -> str:
    """
    Hash password using SHA256.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password as hex string
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored hash to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    return hash_password(plain_password) == hashed_password


def generate_csrf_token() -> str:
    """
    Generate a secure CSRF token.
    
    Returns:
        Random hex token
    """
    return secrets.token_hex(32)
