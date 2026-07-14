from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt


class JwtService:
    def __init__(
        self, secret: str, algorithm: str = "HS256", expire_minutes: int = 1440
    ) -> None:
        self.secret = secret
        self.algorithm = algorithm
        self.expire_minutes = expire_minutes

    def create_token(self, user_id: str, username: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.expire_minutes)
        payload = {
            "sub": str(user_id),
            "username": username,
            "exp": expire,
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict | None:
        try:
            return jwt.decode(token, self.secret, algorithms=[self.algorithm])
        except JWTError:
            return None
