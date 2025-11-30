from fastapi import FastAPI
from router import router
app = FastAPI()
import ssl
import certifi
# import aiohttp
import aiohttp
import asyncio

ssl_ctx = ssl.create_default_context(cafile=certifi.where())
app.include_router(router)

async def fetch_huggingface_data():
        connector = aiohttp.TCPConnector(ssl=False) # Disables SSL verification
        async with aiohttp.ClientSession(connector=connector) as client:
            async with client.get("https://huggingface.co/api/models") as response:
                return await response.json()

if __name__ == "__main__":
        data = asyncio.run(fetch_huggingface_data())
        print(data)