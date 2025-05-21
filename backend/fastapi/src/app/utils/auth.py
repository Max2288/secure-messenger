from jose import JWTError, jwt

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.app.settings import Settings
from src.user.depends import get_user_repository
from src.user.models import User
from src.user.repositories import UserRepository

security = HTTPBearer()

settings = Settings()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    repo: UserRepository = Depends(get_user_repository),
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise ValueError("No subject")
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await repo.get_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
