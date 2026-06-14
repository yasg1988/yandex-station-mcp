from __future__ import annotations

import asyncio
import base64
import json
import os
import pickle
import re
import time
from pathlib import Path
from typing import Any

from aiohttp import ClientSession


MASK_EN = "0123456789abcdef-"
MASK_RU = "оеаинтсрвлкмдпуяы"

NON_SPEAKER_PLATFORMS = {"saturn", "mike", "cherry"}

IOT_TYPES = {
    "on": "devices.capabilities.on_off",
    "volume": "devices.capabilities.range",
    "pause": "devices.capabilities.toggle",
    "mute": "devices.capabilities.toggle",
    "channel": "devices.capabilities.range",
}


def load_env_file(path: str | Path) -> None:
    env_path = Path(path)
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def encode_uid(uid: str) -> str:
    return "".join(MASK_RU[MASK_EN.index(ch)] for ch in uid)


def has_quasar(device: dict[str, Any]) -> bool:
    if device.get("sharing_info"):
        return False
    info = device.get("quasar_info")
    if not info:
        return False
    return info.get("platform") not in NON_SPEAKER_PLATFORMS


def scenario_speaker_tts(name: str, trigger: str, device_id: str, text: str) -> dict[str, Any]:
    return {
        "name": name,
        "icon": "home",
        "triggers": [{"trigger": {"type": "scenario.trigger.voice", "value": trigger}}],
        "steps": [
            {
                "type": "scenarios.steps.actions.v2",
                "parameters": {
                    "items": [
                        {
                            "id": device_id,
                            "type": "step.action.item.device",
                            "value": {
                                "id": device_id,
                                "item_type": "device",
                                "capabilities": [
                                    {
                                        "type": "devices.capabilities.quasar",
                                        "state": {
                                            "instance": "tts",
                                            "value": {"text": text},
                                        },
                                    }
                                ],
                            },
                        }
                    ]
                },
            }
        ],
    }


def scenario_speaker_action(name: str, trigger: str, device_id: str, action: str) -> dict[str, Any]:
    return {
        "name": name,
        "icon": "home",
        "triggers": [{"trigger": {"type": "scenario.trigger.voice", "value": trigger}}],
        "steps": [
            {
                "type": "scenarios.steps.actions.v2",
                "parameters": {
                    "items": [
                        {
                            "id": device_id,
                            "type": "step.action.item.device",
                            "value": {
                                "id": device_id,
                                "item_type": "device",
                                "capabilities": [
                                    {
                                        "type": "devices.capabilities.quasar.server_action",
                                        "state": {
                                            "instance": "text_action",
                                            "value": action,
                                        },
                                    }
                                ],
                            },
                        }
                    ]
                },
            }
        ],
    }


class YandexSession:
    def __init__(
        self,
        session: ClientSession,
        *,
        x_token: str | None = None,
        music_token: str | None = None,
        cookie: str | None = None,
        domain: str | None = None,
    ):
        self._session = session
        setattr(session.cookie_jar, "_quote_cookie", False)
        self.x_token = x_token
        self.music_token = music_token
        self.domain = domain
        self.csrf_token: str | None = None
        self.auth_headers: dict[str, str] | None = None
        self.auth_json: dict[str, Any] | None = None
        self.last_ts = 0.0

        if cookie:
            raw = base64.b64decode(cookie)
            getattr(session.cookie_jar, "_cookies").clear()
            session.cookie_jar._cookies = pickle.loads(raw)
            session.cookie_jar.clear(lambda _: False)

    @property
    def cookie(self) -> str:
        raw = pickle.dumps(getattr(self._session.cookie_jar, "_cookies"), pickle.HIGHEST_PROTOCOL)
        return base64.b64encode(raw).decode()

    def _url(self, url: str) -> str:
        if self.domain:
            return url.replace("yandex.ru", self.domain)
        return url

    async def _request_raw(self, method: str, url: str, **kwargs):
        kwargs.setdefault("timeout", 15)
        return await getattr(self._session, method)(self._url(url), **kwargs)

    async def get_qr(self) -> str:
        response = await self._request_raw("get", "https://passport.yandex.ru/pwl-yandex")
        response.raise_for_status()
        html = await response.text()
        match = re.search(r'__CSRF__ = "([^"]+)', html)
        if not match:
            raise RuntimeError("не удалось получить CSRF для QR-авторизации")

        self.auth_headers = {"X-CSRF-Token": match[1]}
        response = await self._request_raw(
            "post",
            "https://passport.yandex.ru/pwl-yandex/api/passport/auth/password/submit",
            json={"retpath": "https://passport.yandex.ru/"},
            headers=self.auth_headers,
        )
        response.raise_for_status()
        self.auth_json = await response.json()

        response = await self._request_raw(
            "post",
            "https://passport.yandex.ru/pwl-yandex/api/passport/auth/magic/code",
            data={
                "location_id": "0",
                "magic_track_id": self.auth_json["track_id"],
                "track_id": "",
            },
            headers=self.auth_headers,
        )
        response.raise_for_status()
        data = await response.json()
        return data["link"]

    async def login_qr(self) -> dict[str, Any] | None:
        if not self.auth_json or not self.auth_headers:
            raise RuntimeError("QR-авторизация не начата")

        response = await self._request_raw(
            "post",
            "https://passport.yandex.ru/pwl-yandex/api/passport/auth/magic/code/status",
            json=self.auth_json,
            headers=self.auth_headers,
        )
        response.raise_for_status()
        data = await response.json()
        if data.get("state") != "otp_auth_finished":
            return None

        response = await self._request_raw(
            "post",
            "https://passport.yandex.ru/pwl-yandex/api/passport/sessions/get_session",
            data={"track_id": data["trackId"]},
            headers=self.auth_headers,
        )
        response.raise_for_status()
        return await self.login_cookies()

    async def login_cookies(self, cookies: str | None = None) -> dict[str, Any]:
        host = "passport.yandex.ru"
        if cookies is None:
            cookies = "; ".join(
                f"{c.key}={c.value}"
                for c in self._session.cookie_jar
                if c["domain"].endswith("yandex.ru")
            )
        elif cookies.startswith("["):
            raw = json.loads(cookies)
            host = next(item["domain"] for item in raw if item["domain"].startswith(".yandex."))
            cookies = "; ".join(f"{item['name']}={item['value']}" for item in raw)

        response = await self._request_raw(
            "post",
            "https://mobileproxy.passport.yandex.net/1/bundle/oauth/token_by_sessionid",
            data={
                "client_id": "c0ebe342af7d48fbbbfcf2d2eedb8f9e",
                "client_secret": "ad0a908f0aa341a182a37ecd75bc319e",
            },
            headers={"Ya-Client-Host": host, "Ya-Client-Cookie": cookies},
        )
        data = await response.json()
        if "access_token" not in data:
            raise RuntimeError(f"Яндекс не вернул OAuth token: {data}")
        return await self.validate_token(data["access_token"])

    async def validate_token(self, x_token: str) -> dict[str, Any]:
        response = await self._request_raw(
            "get",
            "https://mobileproxy.passport.yandex.net/1/bundle/account/short_info/?avatar_size=islands-300",
            headers={"Authorization": f"OAuth {x_token}"},
        )
        data = await response.json()
        data["x_token"] = x_token
        if data.get("status") != "ok":
            raise RuntimeError(f"токен Яндекса не прошел проверку: {data}")
        self.x_token = x_token
        return data

    async def login_token(self, x_token: str) -> bool:
        response = await self._request_raw(
            "post",
            "https://mobileproxy.passport.yandex.net/1/bundle/auth/x_token/",
            data={"type": "x-token", "retpath": "https://www.yandex.ru"},
            headers={"Ya-Consumer-Authorization": f"OAuth {x_token}"},
        )
        data = await response.json()
        if data.get("status") != "ok":
            return False
        response = await self._request_raw(
            "get",
            f"{data['passport_host']}/auth/session/",
            params={"track_id": data["track_id"]},
            allow_redirects=False,
        )
        return "/auth/finish" in (response.headers.get("Location") or "")

    async def refresh_cookies(self) -> bool:
        response = await self._request_raw("get", "https://yandex.ru/quasar?storage=1")
        data = await response.json()
        if data.get("storage", {}).get("user", {}).get("uid"):
            return True
        if not self.x_token:
            return False
        return await self.login_token(self.x_token)

    async def request(self, method: str, url: str, retry: int = 2, **kwargs):
        while (delay := self.last_ts + 0.2 - time.time()) > 0:
            await asyncio.sleep(delay)
        self.last_ts = time.time()

        if method != "get":
            if self.csrf_token is None:
                response = await self._request_raw("get", "https://yandex.ru/quasar")
                html = await response.text()
                match = re.search('"csrfToken2":"(.+?)"', html)
                if not match:
                    raise RuntimeError("не удалось получить CSRF токен Яндекса")
                self.csrf_token = match[1]
            kwargs["headers"] = {"x-csrf-token": self.csrf_token}

        response = await self._request_raw(method, url, **kwargs)
        if response.status == 200:
            return response
        if response.status == 401 and retry:
            await self.refresh_cookies()
            return await self.request(method, url, retry - 1, **kwargs)
        if response.status == 403 and retry:
            self.csrf_token = None
            return await self.request(method, url, retry - 1, **kwargs)

        body = await response.text()
        raise RuntimeError(f"{url} вернул HTTP {response.status}: {body[:500]}")

    async def get(self, url: str, **kwargs):
        return await self.request("get", url, **kwargs)

    async def post(self, url: str, **kwargs):
        return await self.request("post", url, **kwargs)

    async def put(self, url: str, **kwargs):
        return await self.request("put", url, **kwargs)


class YandexStationClient:
    def __init__(self, session: YandexSession):
        self.session = session
        self.devices: list[dict[str, Any]] = []
        self.scenarios: list[dict[str, Any]] = []

    async def init(self) -> None:
        response = await self.session.get("https://iot.quasar.yandex.ru/m/v3/user/devices", timeout=15)
        data = await response.json()
        if data.get("status") != "ok":
            raise RuntimeError(f"не удалось получить устройства Яндекса: {data}")

        self.devices = []
        for house in data.get("households", []):
            self.devices.extend({**device, "house_name": house.get("name")} for device in house.get("all", []))

        await self.load_scenarios()
        await self.ensure_speaker_scenarios()

    @property
    def speakers(self) -> list[dict[str, Any]]:
        return [device for device in self.devices if has_quasar(device) and device.get("capabilities")]

    async def load_scenarios(self) -> None:
        response = await self.session.get("https://iot.quasar.yandex.ru/m/user/scenarios")
        data = await response.json()
        if data.get("status") != "ok":
            raise RuntimeError(f"не удалось получить сценарии Яндекса: {data}")
        self.scenarios = data.get("scenarios", [])

    async def ensure_speaker_scenarios(self) -> None:
        hashes: dict[str, str] = {}
        for scenario in self.scenarios:
            try:
                hashes[scenario["triggers"][0]["value"]] = scenario["id"]
            except Exception:
                pass

        for speaker in self.speakers:
            device_id = speaker["id"]
            trigger = encode_uid(device_id)
            speaker["scenario_id"] = hashes.get(trigger) or await self.add_scenario(device_id, trigger)

    async def add_scenario(self, device_id: str, trigger: str) -> str:
        payload = scenario_speaker_tts("ХА " + device_id, trigger, device_id, "пустышка")
        response = await self.session.post("https://iot.quasar.yandex.ru/m/v4/user/scenarios", json=payload)
        data = await response.json()
        if data.get("status") != "ok":
            raise RuntimeError(f"не удалось создать служебный сценарий: {data}")
        return data["scenario_id"]

    def select_speaker(self, station: str | None = None) -> dict[str, Any]:
        speakers = self.speakers
        if not speakers:
            raise RuntimeError("в аккаунте не найдены Яндекс Станции с облачным управлением")

        station = station or os.environ.get("YANDEX_STATION_ID") or os.environ.get("YANDEX_STATION_NAME") or ""
        station = station.strip().lower()
        if not station:
            return speakers[0]

        for speaker in speakers:
            values = {
                str(speaker.get("id", "")).lower(),
                str(speaker.get("name", "")).lower(),
                str(speaker.get("quasar_info", {}).get("device_id", "")).lower(),
                str(speaker.get("house_name", "")).lower(),
            }
            if station in values:
                return speaker
        raise RuntimeError(f"станция не найдена: {station}")

    def list_scenarios(self, include_service: bool = False) -> list[dict[str, Any]]:
        return [
            {
                "id": scenario.get("id"),
                "name": scenario.get("name"),
                "icon": scenario.get("icon"),
                "triggers": [
                    trigger.get("value")
                    for trigger in scenario.get("triggers", [])
                    if isinstance(trigger, dict)
                ],
            }
            for scenario in self.scenarios
            if include_service or not str(scenario.get("name", "")).startswith("ХА ")
        ]

    def select_scenario(self, scenario: str) -> dict[str, Any]:
        query = scenario.strip().lower()
        for item in self.scenarios:
            values = {
                str(item.get("id", "")).lower(),
                str(item.get("name", "")).lower(),
            }
            if query in values:
                return item
        raise RuntimeError(f"сценарий не найден: {scenario}")

    async def send_text(self, text: str, *, station: str | None = None, is_tts: bool = False) -> dict[str, Any]:
        device = self.select_speaker(station)
        device_id = device["id"]
        scenario_id = device.get("scenario_id")
        if not scenario_id:
            raise RuntimeError("для станции нет служебного сценария")

        trigger = encode_uid(device_id)
        name = "ХА " + device_id
        payload = scenario_speaker_tts(name, trigger, device_id, text) if is_tts else scenario_speaker_action(name, trigger, device_id, text)

        response = await self.session.put(f"https://iot.quasar.yandex.ru/m/v4/user/scenarios/{scenario_id}", json=payload)
        data = await response.json()
        if data.get("status") != "ok":
            raise RuntimeError(f"не удалось обновить сценарий: {data}")

        response = await self.session.post(f"https://iot.quasar.yandex.ru/m/user/scenarios/{scenario_id}/actions")
        data = await response.json()
        if data.get("status") != "ok":
            raise RuntimeError(f"не удалось запустить сценарий: {data}")

        return {"ok": True, "station": public_speaker(device), "text": text, "tts": is_tts}

    async def command(self, text: str, station: str | None = None) -> dict[str, Any]:
        return await self.send_text(text, station=station, is_tts=False)

    async def say(self, text: str, station: str | None = None) -> dict[str, Any]:
        return await self.send_text(text, station=station, is_tts=True)

    async def volume(self, level: float, station: str | None = None) -> dict[str, Any]:
        level = max(0.0, min(1.0, float(level)))
        value = round(level * 10)
        return await self.command(f"громкость на {value}", station=station)

    async def notify(self, text: str, volume: float | None = 0.4, station: str | None = None) -> dict[str, Any]:
        result: dict[str, Any] = {"ok": True, "steps": []}
        if volume is not None:
            result["steps"].append(await self.volume(volume, station=station))
        result["steps"].append(await self.say(text, station=station))
        return result

    async def play(self, station: str | None = None) -> dict[str, Any]:
        return await self.command("продолжить", station=station)

    async def pause(self, station: str | None = None) -> dict[str, Any]:
        return await self.command("пауза", station=station)

    async def next(self, station: str | None = None) -> dict[str, Any]:
        return await self.command("следующий трек", station=station)

    async def previous(self, station: str | None = None) -> dict[str, Any]:
        return await self.command("прошлый трек", station=station)

    async def stop(self, station: str | None = None) -> dict[str, Any]:
        return await self.command("останови", station=station)

    async def timer(self, minutes: int, text: str | None = None, station: str | None = None) -> dict[str, Any]:
        minutes = max(1, int(minutes))
        suffix = f" {text}" if text else ""
        return await self.command(f"поставь таймер на {minutes} минут{suffix}", station=station)

    async def alarm(self, time_text: str, text: str | None = None, station: str | None = None) -> dict[str, Any]:
        suffix = f" {text}" if text else ""
        return await self.command(f"поставь будильник на {time_text}{suffix}", station=station)

    async def reminder(self, text: str, time_text: str, station: str | None = None) -> dict[str, Any]:
        return await self.command(f"напомни {time_text}: {text}", station=station)

    async def weather(self, station: str | None = None) -> dict[str, Any]:
        return await self.command("какая погода", station=station)

    async def news(self, station: str | None = None) -> dict[str, Any]:
        return await self.command("включи новости", station=station)

    async def run_scenario(self, scenario: str) -> dict[str, Any]:
        item = self.select_scenario(scenario)
        scenario_id = item["id"]
        response = await self.session.post(f"https://iot.quasar.yandex.ru/m/user/scenarios/{scenario_id}/actions")
        data = await response.json()
        if data.get("status") != "ok":
            raise RuntimeError(f"не удалось запустить сценарий: {data}")
        return {"ok": True, "scenario": {"id": scenario_id, "name": item.get("name")}}

    def diagnostics(self, station: str | None = None) -> dict[str, Any]:
        selected = self.select_speaker(station)
        return {
            "ok": True,
            "default_station": public_speaker(selected),
            "speakers_count": len(self.speakers),
            "devices_count": len(self.devices),
            "scenarios_count": len(self.scenarios),
            "token_file": str(token_file_path()),
            "env": {
                "YANDEX_STATION_ID": bool(os.environ.get("YANDEX_STATION_ID")),
                "YANDEX_STATION_NAME": bool(os.environ.get("YANDEX_STATION_NAME")),
                "YANDEX_TOKEN_FILE": bool(os.environ.get("YANDEX_TOKEN_FILE")),
                "YANDEX_DOMAIN": bool(os.environ.get("YANDEX_DOMAIN")),
            },
        }


def public_speaker(speaker: dict[str, Any]) -> dict[str, Any]:
    info = speaker.get("quasar_info") or {}
    return {
        "id": speaker.get("id"),
        "name": speaker.get("name"),
        "house_name": speaker.get("house_name"),
        "online": speaker.get("online"),
        "platform": info.get("platform"),
        "device_id": info.get("device_id"),
        "scenario_ready": bool(speaker.get("scenario_id")),
    }


def token_file_path() -> Path:
    load_env_file(Path(__file__).with_name(".env"))
    raw = os.environ.get("YANDEX_TOKEN_FILE") or str(Path(__file__).with_name("yandex_tokens.json"))
    return Path(raw)


def read_tokens() -> dict[str, Any]:
    path = token_file_path()
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    if token := os.environ.get("YANDEX_X_TOKEN"):
        return {"x_token": token}
    raise RuntimeError(
        "нет токена Яндекса. Запустите: python yandex_station_mcp\\auth_qr.py"
    )


def write_tokens(data: dict[str, Any]) -> None:
    path = token_file_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


async def with_client() -> YandexStationClient:
    load_env_file(Path(__file__).with_name(".env"))
    tokens = read_tokens()
    session = ClientSession()
    yandex = YandexSession(
        session,
        x_token=tokens.get("x_token"),
        music_token=tokens.get("music_token"),
        cookie=tokens.get("cookie"),
        domain=os.environ.get("YANDEX_DOMAIN") or None,
    )
    await yandex.refresh_cookies()
    if yandex.x_token:
        write_tokens({"x_token": yandex.x_token, "music_token": yandex.music_token, "cookie": yandex.cookie})
    client = YandexStationClient(yandex)
    await client.init()
    return client


async def close_client(client: YandexStationClient) -> None:
    await client.session._session.close()


async def run_with_client(coro):
    client = await with_client()
    try:
        return await coro(client)
    finally:
        await close_client(client)
