#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 lurkzies
# SPDX-License-Identifier: MIT
"""CI sanity checks: every example built to a non-empty SVG (inline icons and captions, no HTML labels) and PNG.

    python scripts/check.py <folder containing the built outputs>
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
out = Path(sys.argv[1])
bad = []
sources = sorted((ROOT / "examples").glob("*.mmd"))
if not sources:
    bad.append("no example sources found")
for src in sources:
    svg, png = out / f"{src.stem}.svg", out / f"{src.stem}.png"
    for f in (svg, png):
        if not f.is_file() or f.stat().st_size < 1000:
            bad.append(f"missing or tiny: {f}")
    if svg.is_file():
        text = svg.read_text(encoding="utf-8")
        if "<foreignObject" in text:
            bad.append(f"HTML labels in {svg}")
        if "#049FD9" not in text or "<text" not in text:
            bad.append(f"icons or captions missing in {svg}")
        if "<image" in text:
            bad.append(f"nested image left in {svg} (Typst would drop its text)")
    if png.is_file() and not png.read_bytes().startswith(b"\x89PNG"):
        bad.append(f"not a PNG: {png}")
print("\n".join(bad) or f"ok: {len(sources)} examples")
sys.exit(1 if bad else 0)
