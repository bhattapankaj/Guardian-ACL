"""
Encryption utilities for securely storing Fitbit OAuth tokens.
Uses Fernet symmetric encryption from cryptography library.
"""

from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv()

# Get encryption key from environment
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY not found in environment variables!")

# Initialize Fernet cipher
cipher = Fernet(ENCRYPTION_KEY.encode())


def encrypt_token(token: str) -> str:
    """
    Encrypt a token for secure storage in database.
    
    Args:
        token (str): Plain text token to encrypt
    
    Returns:
        str: Encrypted token (safe to store in database)
    """
    if not token:
        raise ValueError("Token cannot be empty")
    
    encrypted = cipher.encrypt(token.encode())
    return encrypted.decode()


def decrypt_token(encrypted_token: str) -> str:
    """
    Decrypt a token for use in API calls.
    
    Args:
        encrypted_token (str): Encrypted token from database
    
    Returns:
        str: Decrypted plain text token
    """
    if not encrypted_token:
        raise ValueError("Encrypted token cannot be empty")
    
    decrypted = cipher.decrypt(encrypted_token.encode())
    return decrypted.decode()


# Example usage (for testing only - remove in production)
if __name__ == "__main__":
    # Test encryption/decryption
    test_token = "test_access_token_12345"
    
    encrypted = encrypt_token(test_token)
    print(f"Original:  {test_token}")
    print(f"Encrypted: {encrypted}")
    
    decrypted = decrypt_token(encrypted)
    print(f"Decrypted: {decrypted}")
    
    assert test_token == decrypted, "Encryption/decryption failed!"
    print("✅ Encryption test passed!")
