from typing import Annotated

import jwt
from fastapi import Header

from app import ENV, JWT_SECRET_KEY
from app.utils.errors import UnauthorizedException401


# Autorization header
async def authorize(authorization: Annotated[str, Header()] = None) -> str:
    """Authorize requests."""
    credentials_exception = UnauthorizedException401("Could not validate credentials.")

    if ENV == "development":
        return "user_id"

    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    return user_id


async def authorize_interview():
    """Authorize interview requests."""
    pass
