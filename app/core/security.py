import secrets
import hashlib
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_salt() -> str:
    return secrets.token_hex(32)


def hash_password(password: str, salt: str) -> str:
    salted_password = f"{password}{salt}"
    return pwd_context.hash(salted_password)


def verify_password(plain_password: str, salt: str, hashed_password: str) -> bool:
    salted_password = f"{plain_password}{salt}"
    return pwd_context.verify(salted_password, hashed_password)
