---
name: yandex-station-control
description: Управление Яндекс Станцией через отдельный MCP-сервер: музыка, радио, громкость, пауза, следующий/предыдущий трек, TTS и текстовые команды Алисе.
---

# Yandex Station Control

Используйте MCP-сервер `yandex-station`, если он доступен.

## Инструменты

- статус и список колонок: `station_list`, `station_status`
- выбранная колонка и диагностика: `station_default`, `station_diagnostics`
- текстовая команда Алисе: `station_command`
- произнести текст: `station_say`, уведомление с громкостью: `station_notify`
- громкость: `station_volume`
- воспроизведение: `station_play`, `station_pause`, `station_stop`, `station_next`, `station_previous`
- радио: `station_radio`
- музыка: `station_music`
- таймеры, будильники, напоминания: `station_timer`, `station_alarm`, `station_reminder`
- быстрые запросы: `station_weather`, `station_news`
- сценарии Яндекс Умного дома: `station_scenario_list`, `station_scenario_run`

## Соответствие русских команд

- `включи радио Европа плюс` -> `station_radio(name="Европа плюс")`
- `включи мою волну` -> `station_music(query="мою волну")`
- `поставь музыку` -> `station_music(query="музыку")`
- `пауза`, `останови музыку` -> `station_pause`
- `останови`, `выключи музыку` -> `station_stop`
- `продолжи` -> `station_play`
- `следующий трек` -> `station_next`
- `предыдущий трек` -> `station_previous`
- `громкость 30 процентов` -> `station_volume(level=0.3)`
- `скажи через колонку ...` -> `station_say(text="...")`
- `уведомь через колонку ...` -> `station_notify(text="...", volume=0.4)`
- `поставь таймер на 10 минут` -> `station_timer(minutes=10)`
- `поставь будильник на 7:30` -> `station_alarm(time_text="7:30")`
- `напомни завтра в 9 купить хлеб` -> `station_reminder(text="купить хлеб", time_text="завтра в 9")`
- `какая погода` -> `station_weather`
- `включи новости` -> `station_news`
- `запусти сценарий ...` -> сначала `station_scenario_list`, затем `station_scenario_run(scenario="точное имя или id")`

## Выбор колонки

Если пользователь не указал колонку, используйте дефолтную из переменных `YANDEX_STATION_ID` или `YANDEX_STATION_NAME`, иначе первую доступную колонку аккаунта. Если колонок несколько и команда чувствительная к месту воспроизведения, сначала вызовите `station_list`.

Для диагностики без раскрытия токенов используйте `station_diagnostics`.

## Безопасность

Не выводите и не сохраняйте в ответах токены Яндекса, cookies или содержимое `yandex_tokens.json`.

## Ограничения

Это неофициальный API. Облачное управление хорошо отправляет команды, но не гарантирует точную обратную связь о текущем треке и фактической громкости.
