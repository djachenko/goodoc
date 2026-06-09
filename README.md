# goodoc

Upload `.docx`, `.xlsx`, `.pptx`, and `.pptm` files to Google Drive with automatic conversion to native Google formats (Docs / Sheets / Slides). Integrates into macOS Finder as a right-click Quick Action.

**Typical workflow:** got a file to review → right-click → opens in Google Docs. No Word, no drag-and-drop.

---

## Requirements

- macOS
- Python 3.10+
- [pipx](https://pipx.pypa.io/)
- A Google Cloud project with **Drive API** enabled and an OAuth 2.0 Desktop credentials file

---

## Installation

```bash
pipx install git+https://github.com/djachenko/goodoc.git
```

Or clone and install locally:

```bash
git clone https://github.com/djachenko/goodoc.git
cd goodoc
pipx install .
```

---

## Google Cloud setup

1. Go to [console.cloud.google.com](https://console.cloud.google.com) and create or select a project
2. **APIs & Services → Library** → search for `Google Drive API` → **Enable**
3. **APIs & Services → Credentials** → **Create Credentials → OAuth 2.0 Client ID**
   - Application type: **Desktop app**
   - Download the JSON file
4. Place the file at `~/.goodoc/credentials.json`:

```bash
mkdir -p ~/.goodoc
mv ~/Downloads/client_secret_*.json ~/.goodoc/credentials.json
```

On first run, a browser window will open for Google authorization. The token is saved to `~/.goodoc/token.json` — subsequent runs are silent.

---

## Usage

```bash
goodoc file.docx           # upload and open in browser
goodoc file.xlsx --no-open # upload without opening
```

Supported formats:

| Extension | Converts to |
|---|---|
| `.docx` | Google Docs |
| `.xlsx` | Google Sheets |
| `.pptx` | Google Slides |
| `.pptm` | Google Slides |

---

## Finder integration (macOS Quick Action)

1. Open **Automator** → **New Document** → **Quick Action**
2. Set **Workflow receives current**: `files or folders` in `Finder`
3. Add a **Run Shell Script** action, set **Pass input**: `as arguments`
4. Paste the script:

```bash
for f in "$@"; do
    "$(which goodoc)" "$f"
done
```

5. **File → Save** → name it `Open in Google Docs`

Right-click any `.docx`, `.xlsx`, `.pptx`, or `.pptm` in Finder → **Quick Actions → Open in Google Docs**.

> If `which goodoc` doesn't work in Automator, replace it with the full path from `which goodoc` in your terminal (e.g. `/Users/you/.local/bin/goodoc`).

> If the action doesn't appear in the menu: Finder → **Finder menu → Services → Services Preferences…** → find `Open in Google Docs` and enable it.

---

## Revoking access

To re-authorize, delete the token:

```bash
rm ~/.goodoc/token.json
```

---

## License

MIT
