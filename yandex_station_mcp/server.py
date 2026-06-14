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
def station_default(station: str | None = None) -> dict[str, Any]:
    """Показать колонку, которая будет использована по умолчанию или по переданному ID/имени."""
    async def action(client):
        return public_speaker(client.select_speaker(station))

    return run(action)


@mcp.tool()
def station_diagnostics(station: str | None = None) -> dict[str, Any]:
    """Проверить авторизацию, количество устройств, сценарии и выбранную колонку без вывода токенов."""
    return run(lambda client: asyncio.sleep(0, client.diagnostics(station)))


@mcp.tool()
def station_command(text: str, station: str | None = None) -> dict[str, Any]:
    """Отправить Алисе текстовую команду: включи радио, включи музыку, поставь таймер и т.п."""
    return run(lambda client: client.command(text, station=station))


@mcp.tool()
def station_say(text: str, station: str | None = None) -> dict[str, Any]:
    """Произнести текст на колонке голосом Алисы."""
    return run(lambda client: client.say(text, station=station))


@mcp.tool()
def station_notify(text: str, volume: float | None = 0.4, station: str | None = None) -> dict[str, Any]:
    """Произнести уведомление: опционально поставить громкость и сказать текст."""
    return run(lambda client: client.notify(text, volume=volume, station=station))


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
def station_stop(station: str | None = None) -> dict[str, Any]:
    """Остановить текущее воспроизведение или действие Алисы."""
    return run(lambda client: client.stop(station=station))


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


@mcp.tool()
def station_timer(minutes: int, text: str | None = None, station: str | None = None) -> dict[str, Any]:
    """Поставить таймер на заданное число минут."""
    return run(lambda client: client.timer(minutes, text=text, station=station))


@mcp.tool()
def station_alarm(time_text: str, text: str | None = None, station: str | None = None) -> dict[str, Any]:
    """Поставить будильник: time_text может быть '7:30', 'завтра в 8 утра' и т.п."""
    return run(lambda client: client.alarm(time_text, text=text, station=station))


@mcp.tool()
def station_reminder(text: str, time_text: str, station: str | None = None) -> dict[str, Any]:
    """Создать напоминание через Алису."""
    return run(lambda client: client.reminder(text, time_text, station=station))


@mcp.tool()
def station_weather(station: str | None = None) -> dict[str, Any]:
    """Попросить Алису озвучить погоду."""
    return run(lambda client: client.weather(station=station))


@mcp.tool()
def station_news(station: str | None = None) -> dict[str, Any]:
    """Включить новости."""
    return run(lambda client: client.news(station=station))


@mcp.tool()
def station_scenario_list(include_service: bool = False) -> list[dict[str, Any]]:
    """Вернуть список сценариев Яндекс Умного дома. Служебные сценарии скрыты по умолчанию."""
    return run(lambda client: asyncio.sleep(0, client.list_scenarios(include_service=include_service)))


@mcp.tool()
def station_scenario_run(scenario: str) -> dict[str, Any]:
    """Запустить сценарий Яндекса по ID или точному названию."""
    return run(lambda client: client.run_scenario(scenario))


if __name__ == "__main__":
    mcp.run()
