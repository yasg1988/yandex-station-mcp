from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from aiohttp import ClientSession

from client import YandexSession, token_file_path, write_tokens


async def main(path: str) -> None:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    async with ClientSession() as aiohttp_session:
        session = YandexSession(aiohttp_session, cookie=data.get("cookie"))
        session.auth_json = data["auth_json"]
        session.auth_headers = data["auth_headers"]
        result = await session.login_qr()
        if not result:
            print(json.dumps({"ok": False, "reason": "qr_not_confirmed"}, ensure_ascii=False))
            return
        payload = {
            "x_token": result["x_token"],
            "music_token": session.music_token,
            "cookie": session.cookie,
            "display_login": result.get("display_login"),
        }
        write_tokens(payload)
        print(
            json.dumps(
                {
                    "ok": True,
                    "token_file": str(token_file_path()),
                    "display_login": result.get("display_login"),
                },
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))
