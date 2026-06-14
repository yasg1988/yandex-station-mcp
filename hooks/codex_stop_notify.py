from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI = REPO_ROOT / "yandex_station_mcp" / "cli.py"
MESSAGE = "Сообщение от Кодекс: я закончил задачу"
VOLUME = "0.4"
TIMEOUT_SECONDS = 20


def run_cli(*args: str) -> None:
    subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=str(REPO_ROOT),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=TIMEOUT_SECONDS,
        check=False,
    )


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    if os.environ.get("CODEX_YANDEX_NOTIFY_DISABLED") == "1":
        print(json.dumps({"continue": True}, ensure_ascii=False))
        return

    if payload.get("hook_event_name") == "Stop" and payload.get("last_assistant_message"):
        run_cli("volume", VOLUME)
        run_cli("say", MESSAGE)

    print(json.dumps({"continue": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
