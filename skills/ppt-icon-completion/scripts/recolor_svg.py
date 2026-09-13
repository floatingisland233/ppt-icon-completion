#!/usr/bin/env python3
"""Recolor SVG fills to palette role colors."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


FILL_RE = re.compile(
    r'fill\s*=\s*"(?!none)(#[0-9A-Fa-f]{3,8}|black|Black|currentColor)"',
    re.I,
)
STYLE_FILL_RE = re.compile(r"fill\s*:\s*(?!none)(#[0-9A-Fa-f]{3,8}|black|Black|currentColor)", re.I)


def recolor(svg: str, hex_color: str) -> str:
    color = "#" + hex_color.lstrip("#").upper()
    out = FILL_RE.sub(f'fill="{color}"', svg)
    out = STYLE_FILL_RE.sub(f"fill:{color}", out)
    # if no fill attrs, inject on root svg
    if "fill=" not in out.lower():
        out = out.replace("<svg", f'<svg fill="{color}"', 1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", type=Path, required=True)
    ap.add_argument("--palette", type=Path, required=True)
    ap.add_argument("--icons-root", type=Path, required=True)
    args = ap.parse_args()

    inv = json.loads(args.inventory.read_text(encoding="utf-8"))
    pal = json.loads(args.palette.read_text(encoding="utf-8"))["roles"]
    raw = args.icons_root / "raw"
    colored = args.icons_root / "colored"
    colored.mkdir(parents=True, exist_ok=True)

    n = 0
    for icon in inv.get("icons", []):
        iid = icon["id"]
        role = icon.get("theme_color_role", "process_blue")
        hex_color = pal.get(role, "2F6FB8")
        src = raw / f"{iid}.svg"
        if not src.exists():
            print(f"skip missing raw {iid}")
            continue
        text = src.read_text(encoding="utf-8")
        out = recolor(text, hex_color)
        (colored / f"{iid}.svg").write_text(out, encoding="utf-8")
        n += 1
        print(f"colored {iid} -> #{hex_color}")
    print(f"done {n}")


if __name__ == "__main__":
    main()
