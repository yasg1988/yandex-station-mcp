from __future__ import annotations

import argparse
import asyncio
import json

from client import public_speaker, run_with_client


async def main() -> None:
    parser = argparse.ArgumentParser(description="Управление Яндекс Станцией")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list")

    status = sub.add_parser("status")
    status.add_argument("--station")

    default = sub.add_parser("default")
    default.add_argument("--station")

    diagnostics = sub.add_parser("diagnostics")
    diagnostics.add_argument("--station")

    command = sub.add_parser("command")
    command.add_argument("text")
    command.add_argument("--station")

    say = sub.add_parser("say")
    say.add_argument("text")
    say.add_argument("--station")

    notify = sub.add_parser("notify")
    notify.add_argument("text")
    notify.add_argument("--volume", type=float, default=0.4)
    notify.add_argument("--station")

    volume = sub.add_parser("volume")
    volume.add_argument("level", type=float)
    volume.add_argument("--station")

    for name in ("play", "pause", "stop", "next", "previous", "weather", "news"):
        item = sub.add_parser(name)
        item.add_argument("--station")

    radio = sub.add_parser("radio")
    radio.add_argument("name")
    radio.add_argument("--station")

    music = sub.add_parser("music")
    music.add_argument("query", nargs="?", default="моя волна")
    music.add_argument("--station")

    timer = sub.add_parser("timer")
    timer.add_argument("minutes", type=int)
    timer.add_argument("--text")
    timer.add_argument("--station")

    alarm = sub.add_parser("alarm")
    alarm.add_argument("time_text")
    alarm.add_argument("--text")
    alarm.add_argument("--station")

    reminder = sub.add_parser("reminder")
    reminder.add_argument("text")
    reminder.add_argument("time_text")
    reminder.add_argument("--station")

    scenarios = sub.add_parser("scenarios")
    scenarios.add_argument("--all", action="store_true")

    scenario = sub.add_parser("scenario")
    scenario.add_argument("scenario")

    args = parser.parse_args()

    async def action(client):
        if args.cmd == "list":
            return [public_speaker(speaker) for speaker in client.speakers]
        if args.cmd == "status":
            return public_speaker(client.select_speaker(args.station))
        if args.cmd == "default":
            return public_speaker(client.select_speaker(args.station))
        if args.cmd == "diagnostics":
            return client.diagnostics(args.station)
        if args.cmd == "command":
            return await client.command(args.text, station=args.station)
        if args.cmd == "say":
            return await client.say(args.text, station=args.station)
        if args.cmd == "notify":
            return await client.notify(args.text, volume=args.volume, station=args.station)
        if args.cmd == "volume":
            return await client.volume(args.level, station=args.station)
        if args.cmd == "play":
            return await client.play(station=args.station)
        if args.cmd == "pause":
            return await client.pause(station=args.station)
        if args.cmd == "stop":
            return await client.stop(station=args.station)
        if args.cmd == "next":
            return await client.next(station=args.station)
        if args.cmd == "previous":
            return await client.previous(station=args.station)
        if args.cmd == "radio":
            return await client.command(f"включи радио {args.name}", station=args.station)
        if args.cmd == "music":
            return await client.command(f"включи {args.query}", station=args.station)
        if args.cmd == "timer":
            return await client.timer(args.minutes, text=args.text, station=args.station)
        if args.cmd == "alarm":
            return await client.alarm(args.time_text, text=args.text, station=args.station)
        if args.cmd == "reminder":
            return await client.reminder(args.text, args.time_text, station=args.station)
        if args.cmd == "weather":
            return await client.weather(station=args.station)
        if args.cmd == "news":
            return await client.news(station=args.station)
        if args.cmd == "scenarios":
            return client.list_scenarios(include_service=args.all)
        if args.cmd == "scenario":
            return await client.run_scenario(args.scenario)
        raise RuntimeError("unknown command")

    result = await run_with_client(action)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
