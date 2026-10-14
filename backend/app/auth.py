import base64
import hashlib
import hmac
import json
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User

SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "creatcode_jwt_secret_key_change_in_production_2026_xyz_auth_token_secret"
).encode("utf-8")

ACCESS_TOKEN_EXPIRE_SECONDS = 7 * 24 * 3600  # 7 days

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    auto_error=False
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


# Base64 URL helpers
def _b64_url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64_url_decode(data_str: str) -> bytes:
    padding = "=" * (-len(data_str) % 4)
    return base64.urlsafe_b64decode(data_str + padding)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = data.copy()

    now = int(time.time())
    if expires_delta:
        expire_time = now + int(expires_delta.total_seconds())
    else:
        expire_time = now + ACCESS_TOKEN_EXPIRE_SECONDS

    payload["iat"] = now
    payload["exp"] = expire_time

    header_b64 = _b64_url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64_url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))

    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(SECRET_KEY, signing_input, hashlib.sha256).digest()
    sig_b64 = _b64_url_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def decode_access_token(token: str) -> Optional[dict]:
    try:
        parts = token.strip().split(".")
        if len(parts) != 3:
            return None

        header_b64, payload_b64, sig_b64 = parts

        # Verify signature
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(SECRET_KEY, signing_input, hashlib.sha256).digest()
        actual_sig = _b64_url_decode(sig_b64)

        if not hmac.compare_digest(actual_sig, expected_sig):
            return None

        payload_bytes = _b64_url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))

        # Verify expiry
        exp = payload.get("exp")
        if exp and int(time.time()) > int(exp):
            return None

        return payload
    except Exception:
        return None


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or session expired",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception

    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception

    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id_int).first()
    if not user:
        raise credentials_exception

    return user


def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    if not token:
        return None

    payload = decode_access_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        return None

    return db.query(User).filter(User.id == user_id_int).first()
