from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

sys.path.insert(0, str(Path(__file__).resolve().parent))

from client import public_speaker, run_with_client


mcp = FastMCP("yandex-station")


def run(coro):
    return asyncio.run(run_with_client(coro))


@mcp.tool()
def station_list() -> list[dict[str, Any]]:
    """Вернуть список Яндекс Станций аккаунта."""
    return run(lambda client: asyncio.sleep(0, [public_speaker(s) for s in client.speakers]))


@mcp.tool()
def station_status(station: str | None = None) -> dict[str, Any]:
    """Вернуть базовый облачный статус выбранной станции."""
    async def action(client):
        speaker = client.select_speaker(station)
        return public_speaker(speaker)

    return run(action)


@mcp.tool()
def station_command(text: str, station: str | None = None) -> dict[str, Any]:
    """Отправить Алисе текстовую команду: включи радио, включи музыку, поставь таймер и т.п."""
    return run(lambda client: client.command(text, station=station))


@mcp.tool()
def station_say(text: str, station: str | None = None) -> dict[str, Any]:
    """Произнести текст на колонке голосом Алисы."""
    return run(lambda client: client.say(text, station=station))


@mcp.tool()
def station_volume(level: float, station: str | None = None) -> dict[str, Any]:
    """Поставить громкость от 0.0 до 1.0."""
    return run(lambda client: client.volume(level, station=station))


@mcp.tool()
def station_play(station: str | None = None) -> dict[str, Any]:
    """Продолжить воспроизведение."""
    return run(lambda client: client.play(station=station))


@mcp.tool()
def station_pause(station: str | None = None) -> dict[str, Any]:
    """Поставить воспроизведение на паузу."""
    return run(lambda client: client.pause(station=station))


@mcp.tool()
def station_next(station: str | None = None) -> dict[str, Any]:
    """Следующий трек."""
    return run(lambda client: client.next(station=station))


@mcp.tool()
def station_previous(station: str | None = None) -> dict[str, Any]:
    """Предыдущий трек."""
    return run(lambda client: client.previous(station=station))


@mcp.tool()
def station_radio(name: str, station: str | None = None) -> dict[str, Any]:
    """Включить радио по названию."""
    return run(lambda client: client.command(f"включи радио {name}", station=station))


@mcp.tool()
def station_music(query: str = "моя волна", station: str | None = None) -> dict[str, Any]:
    """Включить музыку через Алису."""
    return run(lambda client: client.command(f"включи {query}", station=station))


if __name__ == "__main__":
    mcp.run()
