"""
Authentication module with bcrypt password hashing and verification.
Provides secure password handling for user registration and login.
"""
import bcrypt


def hash_password(password):
    """
    Hash a password using bcrypt with a randomly generated salt.
    
    Args:
        password: Plain text password (string or bytes)
        
    Returns:
        bytes: Bcrypt hashed password (includes salt)
    """
    # Convert password to bytes if it's a string
    if isinstance(password, str):
        password = password.encode('utf-8')
    
    # Generate salt and hash password
    # bcrypt.gensalt() generates a salt with default rounds (12)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    
    return hashed


def verify_password(password, password_hash):
    """
    Verify a password against a stored bcrypt hash.
    
    Args:
        password: Plain text password to verify (string or bytes)
        password_hash: Stored bcrypt hash (bytes or string)
        
    Returns:
        bool: True if password matches, False otherwise
    """
    # Convert password to bytes if it's a string
    if isinstance(password, str):
        password = password.encode('utf-8')
    
    # Convert hash to bytes if it's a string
    if isinstance(password_hash, str):
        password_hash = password_hash.encode('utf-8')
    
    # Verify password against hash
    return bcrypt.checkpw(password, password_hash)

