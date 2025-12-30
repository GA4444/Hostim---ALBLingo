import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from passlib.context import CryptContext
import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))  # 7 days default


def hash_password(password: str) -> str:
	return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
	return pwd_context.verify(password, password_hash)


def create_access_token(subject: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
	expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
	to_encode = {"sub": subject, "exp": expire}
	return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		return payload.get("sub")
	except Exception:
		return None


