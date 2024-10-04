from fastapi import FastAPI

from app.routers import aws, azure, interviews
from app.utils.errors import (
    BaseException,
    base_exception_handler,
    general_exception_handler,
)

app = FastAPI(
    title="Interviews API v1",
    version="0.1.0",
)

app.include_router(interviews.router)
app.include_router(aws.router)
app.include_router(azure.router)


@app.get("/")
async def root():
    return {"message": "Interviews API v1"}


app.add_exception_handler(BaseException, base_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
