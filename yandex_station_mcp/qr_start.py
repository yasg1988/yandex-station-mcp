from __future__ import annotations

import asyncio
import json

from aiohttp import ClientSession

from client import YandexSession


async def main() -> None:
    async with ClientSession() as aiohttp_session:
        session = YandexSession(aiohttp_session)
        link = await session.get_qr()
        payload = {
            "link": link,
            "auth_json": session.auth_json,
            "auth_headers": session.auth_headers,
            "cookie": session.cookie,
        }
        print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
