from fastapi import FastAPI
from router import router
import ssl
import certifi
# import aiohttp
import aiohttp
import asyncio
import logging
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(openapi_url=None)
origins = [
   "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
logger = logging.getLogger('uvicorn.error')