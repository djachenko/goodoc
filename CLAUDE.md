# goodoc — Project Guide

## Цель проекта

CLI-утилита для загрузки офисных файлов в Google Drive с автоконвертацией в нативные Google-форматы. Интегрируется в macOS Finder через Automator Quick Action.

---

## Контекст

Основной сценарий: получил файл на ревью → правый клик → открылось в Google Docs. Без Word, без браузера, без DnD.

Credentials хранит в `~/.goodoc/credentials.json`, токен там же: `~/.goodoc/token.json`.

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
| `.docx` | Google Docs |
| `.xlsx` | Google Sheets |
| `.pptx` | Google Slides |
| `.pptm` | Google Slides |

Добавление нового формата — одна строка в `MIME_MAP` в `src/goodoc/main.py`.

---

## Структура проекта

```
goodoc/
├── CLAUDE.md
├── pyproject.toml
└── src/
    └── goodoc/
        ├── __init__.py
        └── main.py          # вся логика: OAuth, upload, CLI-команда
```

---

## Установка

```bash
pipx install ./goodoc
```

## Использование

```bash
goodoc file.docx          # загрузить и открыть в браузере
goodoc file.xlsx --no-open  # загрузить без открытия
```

---

## OAuth

Credentials: `~/.goodoc/credentials.json` (Desktop app, из Google Cloud Console).  
Токен: `~/.goodoc/token.json` — создаётся при первом запуске.  
Scope: `https://www.googleapis.com/auth/drive.file` — доступ только к файлам созданным этим приложением.

При первом запуске откроется браузер для авторизации. Последующие запуски — молча.

Если Drive API не включён в Cloud Console проекте — включить в APIs & Services → Library.

---

## Automator Quick Action

Для интеграции в правый клик Finder:

1. Automator → New Document → Quick Action
2. "Workflow receives current **files or folders**" in **Finder**
3. Run Shell Script, Pass input: `as arguments`

```bash
for f in "$@"; do
    goodoc "$f"
done
```

---

## Скиллы (детальные гайды)

- `/git` — semantic commits, именование веток
