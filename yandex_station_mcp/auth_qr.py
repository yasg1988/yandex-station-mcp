from __future__ import annotations

import asyncio
import json
import time
import webbrowser

from aiohttp import ClientSession

from client import YandexSession, load_env_file, token_file_path, write_tokens


async def main() -> None:
    load_env_file(__file__.replace("auth_qr.py", ".env"))
    async with ClientSession() as aiohttp_session:
        session = YandexSession(aiohttp_session)
        link = await session.get_qr()
        print("Откройте ссылку и подтвердите вход в Яндекс:")
        print(link)
        try:
            webbrowser.open(link)
        except Exception:
            pass

        deadline = time.time() + 180
        while time.time() < deadline:
            result = await session.login_qr()
            if result:
                payload = {
                    "x_token": result["x_token"],
                    "music_token": session.music_token,
                    "cookie": session.cookie,
                    "display_login": result.get("display_login"),
                }
                write_tokens(payload)
                print(f"Готово. Токены сохранены в {token_file_path()}")
                print(json.dumps({"display_login": result.get("display_login")}, ensure_ascii=False))
                return
            print("Ожидаю подтверждение QR...")
            await asyncio.sleep(3)

    raise SystemExit("Время ожидания QR истекло")


if __name__ == "__main__":
    asyncio.run(main())
