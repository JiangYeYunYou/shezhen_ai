import secrets
import hashlib
import bcrypt


def generate_salt() -> str:
    return secrets.token_hex(32)


def hash_password(password: str, salt: str) -> str:
    salted_password = f"{password}{salt}"
    hashed = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
    bcrypt_hash = bcrypt.hashpw(hashed.encode('utf-8'), bcrypt.gensalt())
    return bcrypt_hash.decode('utf-8')


def verify_password(plain_password: str, salt: str, hashed_password: str) -> bool:
    salted_password = f"{plain_password}{salt}"
    hashed = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
    return bcrypt.checkpw(hashed.encode('utf-8'), hashed_password.encode('utf-8'))
