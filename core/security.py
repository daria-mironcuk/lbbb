from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import hashlib

from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from jose import JWTError, jwt

from app.core.config import settings

# Стабільна схема sha256_crypt без конфліктів версій (замість bcrypt)
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


def _prehash(password: str) -> str:
    """Попереднє хешування пароля перед передачею в CryptContext."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Перевіряє відповідність пароля збереженому хешу."""
    try:
        return pwd_context.verify(_prehash(plain_password), hashed_password)
    except UnknownHashError:
        return False


def get_password_hash(password: str) -> str:
    """Повертає хеш пароля для збереження в БД."""
    return pwd_context.hash(_prehash(password))


def create_access_token(
    data: Dict[str, Any],
    expires_minutes: Optional[int] = None,
) -> str:
    """Створює JWT access-токен із заданим payload та терміном дії."""
    to_encode = data.copy()
    expire_minutes = (
        expires_minutes
        if expires_minutes is not None
        else settings.access_token_expire_minutes
    )
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Декодує JWT токен, повертаючи payload. Кидає JWTError, якщо токен невалідний."""
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        raise