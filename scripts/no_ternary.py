#!/usr/bin/env python3
"""Fail the build on ternary conditional expressions."""

import ast
import sys
from pathlib import Path

DEFAULT_ROOTS = ["src", "tests"]


def find_ternaries(path: Path) -> list[ast.IfExp]:
    tree = ast.parse(path.read_text(), filename=str(path))

    return [node for node in ast.walk(tree) if isinstance(node, ast.IfExp)]


def main() -> int:
    roots = sys.argv[1:]

    if not roots:
        roots = DEFAULT_ROOTS

    found = 0

    for root in roots:
        for path in sorted(Path(root).rglob("*.py")):
            for node in find_ternaries(path):
                print(f"{path}:{node.lineno}:{node.col_offset + 1}: ternary conditional expression")

                found += 1

    if not found:
        return 0

    print(f"\n{found} ternary expression(s) found — use an if/else block instead.", file=sys.stderr)

    return 1


if __name__ == "__main__":
    sys.exit(main())
