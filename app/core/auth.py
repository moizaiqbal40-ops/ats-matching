"""
Password hashing and JWT handling.

Note: we call bcrypt directly rather than going through passlib.
passlib (last released 2020, effectively unmaintained) reads an
internal `bcrypt.__about__.__version__` attribute to detect the
bcrypt version — recent bcrypt releases removed that attribute,
which breaks passlib's version-sniffing and causes spurious
hashing failures. Calling bcrypt's hashpw/checkpw directly avoids
that broken compatibility layer entirely.
"""

from datetime import datetime, timedelta

import bcrypt
import jwt

from app.core.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> str:
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return payload["sub"]
