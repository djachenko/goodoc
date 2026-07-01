#!/bin/bash

set -e

REPO="djachenko/goodoc"
SHELL_RC="$HOME/.zshrc"
[[ "$SHELL" == */bash ]] && SHELL_RC="$HOME/.bashrc"

echo "Installing goodoc..."
pipx install "git+https://github.com/$REPO"

python3 -c "
import re, pathlib
p = pathlib.Path('$SHELL_RC')
t = p.read_text()
t = re.sub(r'\n?# BEGIN goodoc\n.*?# END goodoc\n?', '', t, flags=re.DOTALL)
p.write_text(t)
" 2>/dev/null || true

cat >> "$SHELL_RC" << 'EOF'
# BEGIN goodoc
goodoc-update() {
  pipx upgrade goodoc
}
goodoc-uninstall() {
  pipx uninstall goodoc
  rm -rf "$HOME/Library/Services/Open in Google Docs.workflow"
  rm -rf "$HOME/.goodoc"
  sed -i '' '/# BEGIN goodoc/,/# END goodoc/d' "${ZDOTDIR:-$HOME}/.zshrc"
  echo "goodoc uninstalled. Restart your shell."
}
# END goodoc
EOF

echo "Done. Restart shell or: source $SHELL_RC"
echo "Run 'goodoc <file.docx>' to get started — setup wizard will run on first use."
