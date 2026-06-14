# Yandex Station MCP

Отдельный MCP-сервер для управления Яндекс Станцией / колонкой с Алисой: музыка, радио, громкость, пауза, следующий трек, TTS и текстовые команды Алисе.

Код использует подходы из проекта [AlexxIT/YandexStation](https://github.com/AlexxIT/YandexStation) под лицензией MIT. Это неофициальный API Яндекса, поэтому он может измениться.

## Что умеет

- получить список колонок аккаунта;
- отправить Алисе текстовую команду: `включи радио Европа плюс`;
- произнести текст через колонку;
- поставить громкость;
- play / pause / next / previous;
- быстрые команды для музыки и радио.

## Ограничения

- Это не официальный API Яндекса.
- Нужна авторизация Яндекса через QR.
- Токены хранятся только локально и не должны попадать в GitHub.
- Для облачного управления интеграция создает/обновляет служебный сценарий в аккаунте Яндекса с именем вида `ХА <device_id>`.
- Облачный режим не всегда дает точное состояние воспроизведения. Он хорошо отправляет команды, но не всегда знает, что сейчас играет.

## Установка

```powershell
git clone https://github.com/yasg1988/yandex-station-mcp.git
cd yandex-station-mcp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Авторизация через QR

```powershell
python yandex_station_mcp\auth_qr.py
```

Скрипт покажет ссылку. Откройте ее в браузере, войдите в Яндекс и подтвердите вход. После успешного входа будет создан локальный файл:

```text
yandex_station_mcp/yandex_tokens.json
```

Не публикуйте этот файл.

## Проверка списка станций

```powershell
python yandex_station_mcp\cli.py list
```

## Проверка команды

```powershell
python yandex_station_mcp\cli.py command "включи радио Европа плюс"
```

## Подключение MCP в Codex

Пример `C:\Users\<USER>\.codex\config.toml`:

```toml
[mcp_servers.yandex-station]
command = "python"
args = ["D:\\path\\to\\yandex-station-mcp\\yandex_station_mcp\\server.py"]
startup_timeout_ms = 20000

[mcp_servers.yandex-station.env]
YANDEX_TOKEN_FILE = "D:\\path\\to\\yandex-station-mcp\\yandex_station_mcp\\yandex_tokens.json"
# YANDEX_STATION_ID = "опционально"
```

## MCP tools

- `station_list`
- `station_status`
- `station_command`
- `station_say`
- `station_volume`
- `station_play`
- `station_pause`
- `station_next`
- `station_previous`
- `station_radio`
- `station_music`

## Примеры фраз для Codex

- `включи радио Европа плюс на колонке`
- `сделай Алису потише`
- `поставь громкость Алисы 30 процентов`
- `попроси Алису включить мою волну`
- `скажи через колонку: ужин готов`
