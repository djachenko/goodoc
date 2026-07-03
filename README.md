# goodoc

Upload `.docx`, `.xlsx`, `.pptx`, and `.pptm` files to Google Drive with automatic conversion to native Google formats (Docs / Sheets / Slides). Integrates into macOS Finder as a right-click action.

**Typical workflow:** got a file to review → right-click → opens in Google Docs. No Word, no drag-and-drop.

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

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/djachenko/goodoc/master/install.sh | bash
```

Installs goodoc and adds `goodoc-update` / `goodoc-uninstall` to your shell.

Alternatively, with pipx only (no shell helpers):

```bash
pipx install git+https://github.com/djachenko/goodoc.git
```

---

## First run

On the first run, a setup wizard starts automatically:

1. **Google Cloud credentials** — opens the browser, walks you through creating an OAuth client, prompts for the downloaded JSON file
2. **Authorization** — opens the browser for Google sign-in, saves the token
3. **Finder Quick Action** — installs "Open in Google Docs" to the right-click menu, opens System Settings to enable it

After that, every run is silent.

---

## Update / Uninstall

```bash
goodoc-update      # upgrade to latest version
goodoc-uninstall   # remove goodoc, the Quick Action, and credentials
```

To re-authorize without uninstalling:

```bash
rm ~/.goodoc/token.json
```

---

## License

MIT
