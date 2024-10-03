import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers import aws, azure, interviews
from app.services.broker import Broker
from app.services.redis import RedisService


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:\t  %(message)s")
    RedisService.connect()
    await Broker.connect()
    await Broker.channel()

    yield

    RedisService.disconnect()
    await Broker.disconnect()


app = FastAPI(title="Interviews API", version="0.1.0", lifespan=lifespan)

app.include_router(interviews.router)
app.include_router(aws.router)
app.include_router(azure.router)


@app.get("/")
async def root():
    return {"message": "Interviews API"}
