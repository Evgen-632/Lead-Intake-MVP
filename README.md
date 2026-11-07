# Lead Intake MVP

Небольшому бизнесу важно не терять обращения с сайта. Этот учебный MVP принимает заявку через webhook, сохраняет её в SQLite и фиксирует событие в локальном журнале.

## Архитектура

`POST /lead → Validation → SQLite → Event Log`

FastAPI и Pydantic проверяют JSON, стандартный `sqlite3` сохраняет заявку, а `logging` записывает её идентификатор после успешной транзакции. Время заявки хранится в UTC в формате ISO 8601.

## Технологии и структура

Python 3.10+, FastAPI, Pydantic, Uvicorn, SQLite, logging, pytest и HTTPX (TestClient).

```text
main.py              API и валидация
database.py          создание таблицы и запись заявок
logging_config.py    журнал событий
requirements.txt     зависимости
tests/test_leads.py  автоматические тесты
examples.md          сценарии PowerShell
README.md            инструкция
.gitignore           локальные и служебные файлы
```

## Установка и запуск в Windows PowerShell

В каталоге проекта с установленным Python 3.10 или новее:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Сервер доступен по адресу `http://127.0.0.1:8000`. База `leads.db` создаётся рядом с файлами проекта при запуске. Остановить сервер можно с помощью Ctrl+C.

## Пример заявки

В другом окне PowerShell:

```powershell
$body = @{ name = 'Ирина'; contact = '+79990000000'; source = 'landing'; comment = 'Хочу консультацию по тарифам' } | ConvertTo-Json
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/lead' -Method Post -ContentType 'application/json; charset=utf-8' -Body ([System.Text.Encoding]::UTF8.GetBytes($body))
```

Ответ HTTP 200:

```json
{"status":"ok","lead_id":1,"message":"Заявка успешно сохранена"}
```

Обязателен только непустой `contact`; остальные поля можно опустить. Все поля должны быть строками, пробелы по краям удаляются. Другие сценарии и команды приведены в [examples.md](examples.md).

## Проверка данных и журнала

Выполните из каталога проекта:

```powershell
.\.venv\Scripts\python.exe -c "import sqlite3; c = sqlite3.connect('leads.db'); print(*c.execute('SELECT * FROM leads'), sep='\n'); c.close()"
Get-Content -LiteralPath .\events.log -Encoding UTF8
```

После успешного запроса журнал содержит строку с датой и `New lead saved: <id>`. Контакт в неё не записывается.

## Ошибки

Неверный JSON, отсутствующий или пустой контакт и поля неверного типа возвращают HTTP 400 с пояснением. При ошибке SQLite возвращается HTTP 500 с сообщением `Не удалось сохранить заявку. Попробуйте позже.`; техническая причина записывается в `events.log`.

## Тесты

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Тесты используют временные базу и журнал и не меняют рабочие `leads.db` и `events.log`.

## Ограничения и идеи для v2

Это локальный учебный MVP, не публичный сервис для реальных персональных данных: аутентификация, защита от злоупотреблений, управление хранением данных и развёртывание не реализованы. Для второй версии можно рассмотреть защищённый доступ, политику хранения, резервное копирование и внешний канал уведомлений.
