from fastapi import Request
from fastapi.responses import JSONResponse

from .exceptions import BaseException, InternalServerErrorException


async def base_exception_handler(request: Request, exc: BaseException):
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())


async def general_exception_handler(request: Request, exc: Exception):
    exc = InternalServerErrorException()
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())
