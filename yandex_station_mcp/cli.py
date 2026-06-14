from __future__ import annotations

import argparse
import asyncio
import json

from client import public_speaker, run_with_client


async def main() -> None:
    parser = argparse.ArgumentParser(description="Управление Яндекс Станцией")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list")

    command = sub.add_parser("command")
    command.add_argument("text")
    command.add_argument("--station")

    say = sub.add_parser("say")
    say.add_argument("text")
    say.add_argument("--station")

    volume = sub.add_parser("volume")
    volume.add_argument("level", type=float)
    volume.add_argument("--station")

    args = parser.parse_args()

    async def action(client):
        if args.cmd == "list":
            return [public_speaker(speaker) for speaker in client.speakers]
        if args.cmd == "command":
            return await client.command(args.text, station=args.station)
        if args.cmd == "say":
            return await client.say(args.text, station=args.station)
        if args.cmd == "volume":
            return await client.volume(args.level, station=args.station)
        raise RuntimeError("unknown command")

    result = await run_with_client(action)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
