#!/usr/bin/env python3
"""Resolve icons: cache → builtin pack → list iconfont gaps."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", type=Path, required=True)
    ap.add_argument("--palette", type=Path, required=True)
    ap.add_argument("--icons-root", type=Path, required=True)
    ap.add_argument("--skill-root", type=Path, required=True)
    args = ap.parse_args()

    inv = json.loads(args.inventory.read_text(encoding="utf-8"))
    raw = args.icons_root / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    builtin = args.skill_root / "builtin-icons"
    cache = args.skill_root / "icon-cache"

    items = []
    need_iconfont = []

    for icon in inv.get("icons", []):
        iid = icon["id"]
        dest = raw / f"{iid}.svg"
        source = None
        license_ = "unknown"
        commercial_ok = True

        if dest.exists():
            source = "existing-raw"
            license_ = "user-provided"
        else:
            # cache by builtin_name or id
            name = icon.get("builtin_name") or iid
            for base in (cache, builtin):
                cand = base / f"{name}.svg"
                if cand.exists():
                    shutil.copy2(cand, dest)
                    source = "cache" if base == cache else "builtin"
                    license_ = "MIT-builtin-pack" if source == "builtin" else "cache"
                    break

        if source:
            icon["status"] = "resolved"
            items.append(
                {
                    "id": iid,
                    "source": source,
                    "path": str(dest).replace("\\", "/"),
                    "license": license_,
                    "author": "ppt-icon-completion" if source == "builtin" else "",
                    "project_url": "",
                    "commercial_ok": commercial_ok,
                }
            )
            print(f"resolved {iid} via {source}")
        else:
            icon["status"] = "missing"
            need_iconfont.append(icon)
            print(f"NEED iconfont: {iid} terms={icon.get('search_terms_zh')}")

    sel = {"items": items, "need_iconfont": [
        {"id": i["id"], "search_terms_zh": i.get("search_terms_zh", []), "semantic": i.get("semantic")}
        for i in need_iconfont
    ]}
    out = args.icons_root / "icon_selection.json"
    out.write_text(json.dumps(sel, ensure_ascii=False, indent=2), encoding="utf-8")
    args.inventory.write_text(json.dumps(inv, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out}; need_iconfont={len(need_iconfont)}")


if __name__ == "__main__":
    main()
