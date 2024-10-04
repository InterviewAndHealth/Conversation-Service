import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.app_v1 import app as app_v1
from app.services.broker import Broker
from app.services.redis import RedisService


@asynccontextmanager
async def lifespan(_: FastAPI):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:\t  %(message)s")
    RedisService.connect()
    await Broker.connect()
    await Broker.channel()

    yield

    RedisService.disconnect()
    await Broker.disconnect()


app = FastAPI(
    title="Interviews API",
    version="0.1.0",
    lifespan=lifespan,
    servers=[{"url": "/v1", "description": "Version 1"}],
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/v1", app_v1)


@app.get("/")
async def root():
    return {"message": "Interviews API"}
