from typing import Annotated

from fastapi import Header, HTTPException


# Autorization header
async def authorize(authorization: Annotated[str, Header()] = None):
    """Authorize requests."""
    pass


async def authorize_interview():
    """Authorize interview requests."""
    pass
