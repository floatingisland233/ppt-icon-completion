#!/usr/bin/env python3
"""Sample or write a color palette for icon roles."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image
import numpy as np


DEFAULT_ROLES = {
    "header_navy": "1A4A8C",
    "card_blue": "2B6CB0",
    "card_green": "2FA06E",
    "card_purple": "7A5CA8",
    "card_teal": "2A9B8F",
    "process_blue": "2F6FB8",
    "asis_gray": "7A8A9A",
    "alert_red": "D94545",
    "white": "FFFFFF",
}


def median_hex(im: Image.Image, box) -> str:
    crop = im.crop(box).convert("RGB")
    arr = np.asarray(crop).reshape(-1, 3)
    # drop near-white / near-black
    mask = (arr.max(axis=1) < 245) & (arr.min(axis=1) > 20)
    if mask.sum() < 10:
        pix = arr.mean(axis=0)
    else:
        pix = np.median(arr[mask], axis=0)
    return "{:02X}{:02X}{:02X}".format(int(pix[0]), int(pix[1]), int(pix[2]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=None)
    ap.add_argument("--inventory", type=Path, default=None)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--use-defaults", action="store_true", help="Write default enterprise roles")
    args = ap.parse_args()

    roles = dict(DEFAULT_ROLES)
    notes = "default enterprise roles"

    if args.source and args.source.exists() and args.inventory and args.inventory.exists():
        im = Image.open(args.source).convert("RGB")
        W, H = im.size
        inv = json.loads(args.inventory.read_text(encoding="utf-8"))
        sampled = {}
        for icon in inv.get("icons", []):
            role = icon.get("theme_color_role")
            bbox = icon.get("bbox_norm")
            if not role or not bbox or len(bbox) != 4:
                continue
            l, t, r, b = bbox
            box = (int(l * W), int(t * H), int(r * W), int(b * H))
            if box[2] <= box[0] or box[3] <= box[1]:
                continue
            sampled[role] = median_hex(im, box)
        if sampled:
            roles.update(sampled)
            notes = f"defaults + sampled from {args.source.name}"

    if args.use_defaults and not (args.source and args.inventory):
        notes = "default enterprise roles only"

    payload = {"roles": roles, "sampling_notes": notes}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
