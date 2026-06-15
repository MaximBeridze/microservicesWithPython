from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings

bearer_scheme = HTTPBearer()


def create_access_token(data: dict) -> str:
    """
    Create a signed JWT token from a claims dictionary.

    What you need to do:
      1. Copy `data` into a new dict so you don't mutate the original.
      2. Add an "exp" claim: current UTC time + settings.access_token_expire_minutes.
         Use datetime.now(timezone.utc) + timedelta(minutes=...).
      3. Encode and sign the dict using:
            jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
      4. Return the resulting token string.

    Useful imports (already available above):
        from jose import jwt
        from datetime import datetime, timedelta, timezone
        from app.config import settings

    Example:
        token = create_access_token({"sub": "testuser", "role": "gamer"})
        # → "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

    Once this works, paste the token at https://jwt.io and verify the claims.
    """
    payload = data.copy()
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload["exp"] = expires_at
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    FastAPI dependency — extract and verify the JWT from the Authorization header.

    FastAPI automatically reads the "Authorization: Bearer <token>" header
    and passes it to this function as `credentials.credentials`.

    What you need to do:
      1. Decode and verify the token:
            payload = jwt.decode(
                credentials.credentials,
                settings.secret_key,
                algorithms=[settings.algorithm],
            )
      2. If the token is invalid, expired, or tampered with, jwt.decode raises JWTError.
         Catch it and raise:
            HTTPException(status_code=401, detail="Invalid or expired token")
      3. Return the decoded payload dict.
         It will contain whatever claims were put in by create_access_token,
         e.g. {"sub": "testuser", "role": "gamer", "exp": 1234567890}

    Useful imports (already available above):
        from jose import jwt, JWTError
        from fastapi import HTTPException, status

    After implementing both functions, test with:
        GET /v1/auth/me  →  should return your token's payload
    """
    try:
        return jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
