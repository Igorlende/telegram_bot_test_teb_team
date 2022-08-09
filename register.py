import aiohttp
import asyncio
import json


async def register_user(data):
    url = "http://127.0.0.1:8000/api/register"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=json.dumps(data)) as response:
                text = await response.text()
                return text
    except Exception as ex:
        return ex

"""
loop = asyncio.get_event_loop()
loop.run_until_complete(register_user(json.dumps({"username": "pini",
                                       "password": "asdASD123",
                                       "user_id": 1232321321})))
"""