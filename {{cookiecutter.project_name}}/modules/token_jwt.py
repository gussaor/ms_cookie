from datetime import datetime, timedelta
from typing import Dict

import jwt
from pydantic import ValidationError
from starlette.authentication import AuthenticationError


class TokenJWT:
    def __init__(self):
        self.JWT_SUBJECT = "access"
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # one week
        self.secret_key = "secret"

    def _get_token(self, token: str) -> Dict:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.ALGORITHM])

        except (
            ValidationError,
            jwt.ExpiredSignatureError,
            jwt.PyJWTError,
        ) as validation_error:
            raise AuthenticationError(validation_error)

    def create(
        self,
        data: dict,
        expires_delta: timedelta,
    ) -> str:
        exp = datetime.utcnow() + expires_delta
        data["exp"] = int(exp.timestamp())
        data["sub"] = self.JWT_SUBJECT

        return jwt.encode(data, self.secret_key, algorithm=self.ALGORITHM)

    def get(self, token: str) -> Dict:
        return self._get_token(token=token)

    def get_validation_token(
        self,
        token: str,
    ) -> bool:
        return len(self._get_token(token)) > 0

    def get_user_id_from_token(self, token: str) -> str:
        return self._get_token(token)["id"]

    def get_groups_from_token(self, token: str) -> str:
        return self._get_token(token)["groups"]
