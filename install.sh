#!/bin/bash

set -e

REPO="djachenko/goodoc"
SHELL_RC="$HOME/.zshrc"
[[ "$SHELL" == */bash ]] && SHELL_RC="$HOME/.bashrc"
SHELL_FILE="${XDG_DATA_HOME:-$HOME/.local/share}/goodoc/shell.sh"

echo "Installing goodoc..."
# upgrade if already installed, install otherwise
if pipx list --short 2>/dev/null | grep -q '^goodoc '; then
    pipx upgrade goodoc
else
    pipx install goodoc
fi

# Install Finder Quick Action
echo "Installing Finder Quick Action..."
WORKFLOW="$HOME/Library/Services/Open in Google Docs.workflow/Contents"
mkdir -p "$WORKFLOW"
BASE="https://raw.githubusercontent.com/$REPO/master/workflow/Contents"
curl -fsSL "$BASE/document.wflow" -o "$WORKFLOW/document.wflow"
curl -fsSL "$BASE/Info.plist"     -o "$WORKFLOW/Info.plist"
/System/Library/CoreServices/pbs -update 2>/dev/null || true

# Write shell integration to its own file — never touch the rc again after this.
# Placeholder __SHELL_RC__ is substituted by sed below because the heredoc uses
# single quotes to prevent premature expansion of $variables inside the script body.
mkdir -p "$(dirname "$SHELL_FILE")"
cat > "$SHELL_FILE" << 'SHELLEOF'
goodoc-update() {
  pipx upgrade goodoc
  local workflow="$HOME/Library/Services/Open in Google Docs.workflow/Contents"
  local base="https://raw.githubusercontent.com/djachenko/goodoc/master/workflow/Contents"
  curl -fsSL "$base/document.wflow" -o "$workflow/document.wflow"
  curl -fsSL "$base/Info.plist"     -o "$workflow/Info.plist"
  /System/Library/CoreServices/pbs -update 2>/dev/null || true
}
goodoc-uninstall() {
  pipx uninstall goodoc
  rm -rf "$HOME/Library/Services/Open in Google Docs.workflow"
  rm -rf "${XDG_CONFIG_HOME:-$HOME/.config}/goodoc"
  rm -rf "${XDG_DATA_HOME:-$HOME/.local/share}/goodoc"
  python3 -c "
import pathlib
p = pathlib.Path('__SHELL_RC__')
lines = p.read_text().splitlines(keepends=True)
lines = [l for l in lines if 'goodoc/shell.sh' not in l]
p.write_text(''.join(lines))
" 2>/dev/null || true
  echo "goodoc uninstalled. Restart your shell."
}
SHELLEOF

sed -i '' "s|__SHELL_RC__|$SHELL_RC|g" "$SHELL_FILE"

# Add source line to rc once — idempotent on updates since the line is identical.
python3 -c "
import pathlib
p = pathlib.Path('$SHELL_RC')
t = p.read_text()
line = '[ -f \"$SHELL_FILE\" ] && source \"$SHELL_FILE\"\n'
if line.strip() not in t:
    p.write_text(t.rstrip('\n') + '\n' + line)
" 2>/dev/null || true

echo "Done. Restart shell or: source $SHELL_RC"
echo "Run 'goodoc <file.docx>' to get started — auth wizard will run on first use."
