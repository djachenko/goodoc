# goodoc

![CI](https://github.com/djachenko/goodoc/actions/workflows/tests.yml/badge.svg)
[![PyPI](https://img.shields.io/pypi/v/goodoc.svg)](https://pypi.org/project/goodoc/)
![Python](https://img.shields.io/pypi/pyversions/goodoc.svg)
![License](https://img.shields.io/github/license/djachenko/goodoc.svg)

Upload Office files to Google Drive with automatic conversion to native Google formats (Docs / Sheets / Slides). Integrates into macOS Finder as a right-click action.

**Typical workflow:** got a file to review → right-click → opens in Google Docs. No Word, no drag-and-drop.

---

## Usage

```bash
goodoc file.docx                    # upload and open in browser
goodoc file.xlsx --no-open          # upload without opening
goodoc file.docx file.xlsx file.pptx  # upload multiple files
```

Supported formats:

| Extension | Converts to |
|---|---|
| `.doc`, `.docx` | Google Docs |
| `.xls`, `.xlsx` | Google Sheets |
| `.ppt`, `.pptx`, `.pptm` | Google Slides |

---

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/djachenko/goodoc/master/install.sh | bash
```

Installs goodoc, the Finder Quick Action, and adds `goodoc-update` / `goodoc-uninstall` to your shell.

Alternatively, CLI only (no Quick Action or shell helpers):

```bash
pipx install git+https://github.com/djachenko/goodoc.git
```

---

## First run

On the first run, a setup wizard starts automatically:

1. **Google Cloud credentials** — opens the browser, walks you through creating an OAuth client, prompts for the downloaded JSON file
2. **Authorization** — opens the browser for Google sign-in, saves the token

After that, every run is silent.

Enable the Quick Action in: System Settings → Privacy & Security → Extensions → Finder Extensions.

---

## Update / Uninstall

```bash
goodoc-update      # upgrade to latest version
goodoc-uninstall   # remove goodoc, the Quick Action, and credentials
```

To re-authorize without uninstalling:

```bash
rm ~/.config/goodoc/token.json
```

---

## License

MIT
