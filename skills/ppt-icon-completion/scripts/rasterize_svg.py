#!/usr/bin/env python3
"""Rasterize colored SVGs to transparent PNGs via PyMuPDF."""
from __future__ import annotations

import argparse
from pathlib import Path

import fitz


def svg_to_png(svg_path: Path, png_path: Path, size: int = 256) -> None:
    doc = fitz.open(svg_path)
    try:
        page = doc[0]
        # scale to target size
        rect = page.rect
        scale = size / max(rect.width, rect.height, 1)
        mat = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat, alpha=True)
        png_path.parent.mkdir(parents=True, exist_ok=True)
        pix.save(str(png_path))
    finally:
        doc.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--icons-root", type=Path, required=True)
    ap.add_argument("--size", type=int, default=256)
    args = ap.parse_args()

    colored = args.icons_root / "colored"
    png_dir = args.icons_root / "png"
    png_dir.mkdir(parents=True, exist_ok=True)

    n = 0
    for svg in sorted(colored.glob("*.svg")):
        out = png_dir / f"{svg.stem}.png"
        svg_to_png(svg, out, args.size)
        n += 1
        print(f"raster {svg.name} -> {out.name}")
    print(f"done {n}")


if __name__ == "__main__":
    main()
