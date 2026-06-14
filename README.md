# Yandex Station MCP

Отдельный MCP-сервер для управления Яндекс Станцией / колонкой с Алисой: музыка, радио, громкость, пауза, следующий трек, TTS и текстовые команды Алисе.

Код использует подходы из проекта [AlexxIT/YandexStation](https://github.com/AlexxIT/YandexStation) под лицензией MIT. Это неофициальный API Яндекса, поэтому он может измениться.

## Что умеет

- получить список колонок аккаунта;
- отправить Алисе текстовую команду: `включи радио Европа плюс`;
- произнести текст через колонку;
- произнести уведомление с заданной громкостью;
- поставить громкость;
- play / pause / next / previous;
- stop;
- быстрые команды для музыки и радио.
- таймеры, будильники, напоминания;
- погода и новости;
- список и запуск сценариев Яндекс Умного дома;
- диагностика подключения без вывода токенов.

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
# YANDEX_STATION_NAME = "опционально"
```

Если колонок несколько, можно задать колонку по умолчанию через `YANDEX_STATION_ID` или `YANDEX_STATION_NAME`. Если переменные не заданы, используется первая доступная колонка аккаунта.

## MCP tools

- `station_list`
- `station_status`
- `station_default`
- `station_diagnostics`
- `station_command`
- `station_say`
- `station_notify`
- `station_volume`
- `station_play`
- `station_pause`
- `station_stop`
- `station_next`
- `station_previous`
- `station_radio`
- `station_music`
- `station_timer`
- `station_alarm`
- `station_reminder`
- `station_weather`
- `station_news`
- `station_scenario_list`
- `station_scenario_run`

## CLI команды

```powershell
python yandex_station_mcp\cli.py list
python yandex_station_mcp\cli.py diagnostics
python yandex_station_mcp\cli.py notify "Задача завершена" --volume 0.4
python yandex_station_mcp\cli.py stop
python yandex_station_mcp\cli.py timer 10 --text "проверить духовку"
python yandex_station_mcp\cli.py alarm "7:30"
python yandex_station_mcp\cli.py reminder "купить хлеб" "завтра в 9"
python yandex_station_mcp\cli.py weather
python yandex_station_mcp\cli.py news
python yandex_station_mcp\cli.py scenarios
python yandex_station_mcp\cli.py scenario "Название сценария"
```

## Примеры фраз для Codex

- `включи радио Европа плюс на колонке`
- `сделай Алису потише`
- `поставь громкость Алисы 30 процентов`
- `попроси Алису включить мою волну`
- `скажи через колонку: ужин готов`
- `уведомь через колонку: задача завершена`
- `поставь таймер на 10 минут`
- `поставь будильник на 7:30`
- `напомни завтра в 9 купить хлеб`
- `запусти сценарий Вечер`

## Уведомление Codex через колонку после завершения задачи

В репозитории есть готовый hook-скрипт:

```text
hooks/codex_stop_notify.py
```

Он срабатывает на событии Codex CLI `Stop`, ставит громкость `0.4` и произносит:

```text
Сообщение от Кодекс: я закончил задачу
```

Пример блока для `C:\Users\<USER>\.codex\config.toml`:

```toml
[[hooks.Stop]]

[[hooks.Stop.hooks]]
type = "command"
command = 'python "D:\path\to\yandex-station-mcp\hooks\codex_stop_notify.py"'
timeout = 30
statusMessage = "Уведомляю через Яндекс Станцию"
```

После добавления hook откройте в Codex CLI команду `/hooks` и подтвердите доверие к hook-команде. Это нужно один раз после добавления или изменения hook.

Чтобы временно отключить уведомление без удаления hook, запустите Codex с переменной окружения:

```powershell
$env:CODEX_YANDEX_NOTIFY_DISABLED = "1"
codex
```
