---
name: yandex-station-control
description: Управление Яндекс Станцией через отдельный MCP-сервер: музыка, радио, громкость, пауза, следующий/предыдущий трек, TTS и текстовые команды Алисе.
---

# Yandex Station Control

Используйте MCP-сервер `yandex-station`, если он доступен.

## Инструменты

- статус и список колонок: `station_list`, `station_status`
- текстовая команда Алисе: `station_command`
- произнести текст: `station_say`
- громкость: `station_volume`
- воспроизведение: `station_play`, `station_pause`, `station_next`, `station_previous`
- радио: `station_radio`
- музыка: `station_music`

## Соответствие русских команд

- `включи радио Европа плюс` -> `station_radio(name="Европа плюс")`
- `включи мою волну` -> `station_music(query="мою волну")`
- `поставь музыку` -> `station_music(query="музыку")`
- `пауза`, `останови музыку` -> `station_pause`
- `продолжи` -> `station_play`
- `следующий трек` -> `station_next`
- `предыдущий трек` -> `station_previous`
- `громкость 30 процентов` -> `station_volume(level=0.3)`
- `скажи через колонку ...` -> `station_say(text="...")`

## Безопасность

Не выводите и не сохраняйте в ответах токены Яндекса, cookies или содержимое `yandex_tokens.json`.

## Ограничения

Это неофициальный API. Облачное управление хорошо отправляет команды, но не гарантирует точную обратную связь о текущем треке и фактической громкости.
