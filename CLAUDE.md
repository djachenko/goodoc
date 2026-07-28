# goodoc — Project Guide

## Цель проекта

CLI-утилита для загрузки офисных файлов в Google Drive с автоконвертацией в нативные Google-форматы. Интегрируется в macOS Finder через Automator Quick Action.

---

## Контекст

Основной сценарий: получил файл на ревью → правый клик → открылось в Google Docs. Без Word, без браузера, без DnD.

Credentials хранит в `~/.config/goodoc/credentials.json`, токен там же: `~/.config/goodoc/token.json`.

---

## Стек

| | |
|---|---|
| **Язык** | Python 3.10+ |
| **CLI** | Typer |
| **Google API** | google-api-python-client, google-auth-oauthlib |
| **Установка** | pipx |

---

## Поддерживаемые форматы

| Расширение | Google-формат |
|---|---|
| `.doc`, `.docx` | Google Docs |
| `.xls`, `.xlsx` | Google Sheets |
| `.ppt`, `.pptx`, `.pptm` | Google Slides |

Добавление нового формата — одна строка в `MIME_MAP` в `src/goodoc/drive.py`.

---

## Структура проекта

```
goodoc/
├── CLAUDE.md
├── install.sh               # полная установка: pipx + workflow + shell.sh
├── pyproject.toml
├── workflow/                # шаблон Automator Quick Action (копируется install.sh)
│   └── Contents/
│       ├── document.wflow
│       └── Info.plist
└── src/
    └── goodoc/
        ├── __init__.py
        ├── main.py          # CLI: upload (по умолчанию) / login / logout
        ├── config.py        # пути и scopes
        ├── auth.py          # Auth — получение и обновление токена
        ├── client.py        # встроенный OAuth-клиент автора + хеш ключа доступа
        ├── drive.py         # загрузка в Drive
        └── setup.py         # визард первого запуска (свой Cloud-проект)
```

---

## Установка

```bash
pipx install ./goodoc
```

## Использование

```bash
goodoc file.docx            # загрузить и открыть в браузере
goodoc file.xlsx --no-open  # загрузить без открытия
goodoc login                # авторизоваться без загрузки
goodoc logout               # удалить токен
```

`upload` — команда по умолчанию: `DefaultCommandGroup` в `main.py` подставляет её, если первый аргумент не имя команды. Без этого variadic-аргумент съедает `login`/`logout`.

---

## OAuth

Два источника OAuth-клиента:

| Путь | Когда | Клиент |
|---|---|---|
| Свой проект (по умолчанию) | визард первого запуска | `~/.config/goodoc/credentials.json` |
| Общий клиент автора | `goodoc login --key <KEY>` | `client.py`, проект «gooodoc» |

Токен в обоих случаях: `~/.config/goodoc/token.json`.  
Scope: `https://www.googleapis.com/auth/drive.file` — доступ только к файлам созданным этим приложением.

Общий клиент: Production без верификации — белого списка нет, но user cap **100 авторизаций на весь срок проекта**, необратимо. Снять потолок можно только верификацией, а она требует домена.

**Ключ доступа = `client_secret` общего клиента.** В репозитории лежит только `CLIENT_ID` (публичен по природе — виден в каждом authorization URL) и `ACCESS_KEY_HASH` (sha256, секрет не раскрывает). Секрет подставляется из ключа в рантайме — `client_config(access_key)` в `client.py`. Замерено 2026-07-24: token endpoint Google без `client_secret` отвечает `client_secret is missing`, то есть общий клиент без ключа не работает в принципе — гейт настоящий, а не декоративный. Хеш нужен только для быстрого отказа, чтобы не гонять человека через браузер ради неверного ключа.

Раздавать ключ адресно. Утёкший ключ = доступ к общему клиенту и расход ячеек.

Если Drive API не включён в Cloud Console проекте — включить в APIs & Services → Library.

---

## Automator Quick Action

Шаблон в `workflow/`. Устанавливается автоматически через `install.sh` (curl в `~/Library/Services/`). Обновляется через `goodoc-update`.

После установки включить в: System Settings → Privacy & Security → Extensions → Finder Extensions.

---

## Скиллы (детальные гайды)

- `/git` — semantic commits, именование веток
