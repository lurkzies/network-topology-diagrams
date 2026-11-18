#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 lurkzies
# SPDX-License-Identifier: MIT
"""Build Cisco-style network diagrams from plain Mermaid flowchart sources.

    python build.py diagram.mmd                 # -> diagram.svg
    python build.py diagram.mmd -f png -s 3     # -> diagram.png at 3x
    python build.py examples/                   # every .mmd in the folder
    python build.py --list-icons

Declare nodes with an icon (everything else is ordinary Mermaid):

    ID@{ img: "icon:router", label: "ISP 1\\nPE/CE" }
    ID@{ img: "icon:rack", label: "DMZ\\nWeb Servers" }:::zone-blue

The first label line is bold, further lines grey. `:::zone-<colour>` draws a dashed, tinted
zone box around the node. Requires Python 3.9+ and Node.js 22.13+ (for mermaid-cli).
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
MERMAID_CLI = "@mermaid-js/mermaid-cli@12.2.0"   # pinned: the img node shape needs Mermaid >= 11.3
ICON_H = 84          # rendered icon height in px
LINE = 20            # caption line height
ZONES = {"blue": "#0070C0", "orange": "#ED7D31", "red": "#E02020",
         "green": "#00A050", "purple": "#7B3FBF", "gray": "#6B7280"}
FONT = "Noto Sans, Segoe UI, Helvetica Neue, Helvetica, Arial, sans-serif"

NODE = re.compile(r'^(\s*)(\w+)@\{(.*)\}\s*(?::::zone-(\w+))?\s*$')
ICON_REF = re.compile(r'img:\s*"icon:([\w-]+)"')


class BuildError(Exception):
    """A user-facing error: printed without a traceback."""


def read_text(path):
    return Path(path).read_text(encoding="utf-8")


def icon_names():
    return sorted(p.stem for p in (HERE / "icons").glob("*.svg"))


def icon(name):
    path = HERE / "icons" / f"{name}.svg"
    if not path.is_file():
        raise BuildError(f'unknown icon "{name}". Available: {", ".join(icon_names())}')
    svg = read_text(path)
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
    inner = re.search(r'<svg[^>]*>(.*)</svg>', svg, re.S).group(1)
    return vb, inner


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def node_svg(icon_name, label, zone):
    vb, inner = icon(icon_name)
    ih = ICON_H
    iw = ih * vb[2] / vb[3]
    if iw > ih * 1.7:                      # keep wide icons (server, cloud) in proportion
        iw = ih * 1.7
        ih = iw * vb[3] / vb[2]
    lines = re.split(r'\\n|<br\s*/?>', label) if label else []
    tw = max((len(line) * 9.6 for line in lines), default=0)
    pad = 22 if zone else 8
    w = max(iw, tw) + 2 * pad
    top = pad + (4 if zone else 0)
    h = top + ih + (12 + len(lines) * LINE if lines else 0) + pad
    text = "".join(
        f'<text x="{w/2:.0f}" y="{top + ih + 22 + i*LINE:.0f}" text-anchor="middle" '
        f'font-family="{FONT}" font-size="{16 if i == 0 else 14}" '
        f'font-weight="{700 if i == 0 else 400}" '
        f'fill="{"#111827" if i == 0 else "#4b5563"}">{esc(line)}</text>'
        for i, line in enumerate(lines))
    box = ""
    if zone:
        c = ZONES[zone]
        box = (f'<rect x="2" y="2" width="{w-4:.0f}" height="{h-4:.0f}" rx="14" fill="{c}" '
               f'fill-opacity="0.07" stroke="{c}" stroke-width="3" stroke-dasharray="9 6"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
           f'viewBox="0 0 {w:.0f} {h:.0f}">{box}'
           f'<svg x="{(w-iw)/2:.1f}" y="{top}" width="{iw:.1f}" height="{ih:.1f}" '
           f'viewBox="{" ".join(map(str, vb))}">{inner}</svg>{text}</svg>')
    svg = re.sub(r'\s+', ' ', svg).replace('"', "'")
    uri = "data:image/svg+xml," + urllib.parse.quote(svg, safe="/:,='() ").replace(" ", "%20")
    return uri, round(w), round(h)


def convert(src, name="<input>"):
    """Replace `icon:` nodes with self-contained image nodes; pass everything else through."""
    out = []
    for n, line in enumerate(src.splitlines(), 1):
        if 'img:' not in line or 'icon:' not in line:
            out.append(line)
            continue
        m = NODE.match(line)
        if not m:
            raise BuildError(f'{name}:{n}: cannot parse node. Expected '
                             f'ID@{{ img: "icon:NAME", label: "..." }} optionally followed by :::zone-COLOUR')
        indent, nid, body, zone = m.groups()
        ref = ICON_REF.search(body)
        if not ref:
            raise BuildError(f'{name}:{n}: node {nid} must use img: "icon:NAME"')
        if zone and zone not in ZONES:
            raise BuildError(f'{name}:{n}: unknown zone colour "{zone}". Available: {", ".join(ZONES)}')
        label = re.search(r'label:\s*"([^"]*)"', body)
        try:
            uri, w, h = node_svg(ref.group(1), label.group(1) if label else "", zone)
        except BuildError as e:
            raise BuildError(f"{name}:{n}: {e}") from None
        out.append(f'{indent}{nid}@{{ img: "{uri}", label: "", w: {w}, h: {h}, constraint: "on" }}')
    text = "\n".join(out) + "\n"
    if "linkStyle" not in text:
        text += "    linkStyle default stroke:#1f2937,stroke-width:3px\n"
    if "classDef default" not in text:
        text += "    classDef default fill:none,stroke:none\n"
    return text


SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
DATA_SVG = "data:image/svg+xml,"
TRANSLATE = re.compile(r"translate\(\s*(-?[\d.eE+-]+)(?:[\s,]+(-?[\d.eE+-]+))?\s*\)")


def _offset(transform):
    """(dx, dy) for a pure translate(...) transform string, or None for anything else."""
    if not transform:
        return 0.0, 0.0
    if TRANSLATE.sub("", transform).strip():
        return None
    pairs = TRANSLATE.findall(transform)
    return sum(float(a) for a, _ in pairs), sum(float(b or 0) for _, b in pairs)


def inline_images(svg_text):
    """Replace data-URI <image> nodes with inline SVG, hoisted to the end of the document.

    Typst (and some other renderers) don't resolve fonts for SVG nested as an image, so captions would
    disappear. Inlining puts the text in the main document. The content is hoisted out of Mermaid's node
    groups because Mermaid's stylesheet (`.node path`, `.default rect`, ...) would otherwise recolour it.
    """
    root = ET.fromstring(svg_text)
    hoisted = []

    def walk(el, ox, oy):
        for child in list(el):
            off = _offset(child.get("transform"))
            if off is None:
                continue
            href = child.get("href") or ""
            if child.tag == f"{{{SVG_NS}}}image" and href.startswith(DATA_SVG):
                g = ET.Element(f"{{{SVG_NS}}}g", transform=f"translate({ox + off[0]:g},{oy + off[1]:g})")
                g.append(ET.fromstring(urllib.parse.unquote(href[len(DATA_SVG):])))
                hoisted.append(g)
                el.remove(child)
            else:
                walk(child, ox + off[0], oy + off[1])

    walk(root, 0.0, 0.0)
    root.extend(hoisted)
    return ET.tostring(root, encoding="unicode")


def find_mmdc():
    """Locate mermaid-cli: local install, then PATH, then npx. Returns an argv prefix."""
    local = shutil.which("mmdc", path=str(HERE / "node_modules" / ".bin"))   # honours PATHEXT (mmdc.cmd)
    if local:
        return [local]
    found = shutil.which("mmdc")
    if found:
        return [found]
    npx = shutil.which("npx")
    if npx:
        return [npx, "--yes", MERMAID_CLI]
    raise BuildError("mermaid-cli not found. Run `npm install` in this folder (needs Node.js 22.13+), "
                     "or `npm install -g @mermaid-js/mermaid-cli`.")


def render(mmdc, src_path, dst, scale, no_sandbox):
    src_path = Path(src_path)
    if not src_path.is_file():
        raise BuildError(f"input file not found: {src_path}")
    mmd = convert(read_text(src_path), src_path.name)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d) / "diagram.mmd"
        tmp.write_text(mmd, encoding="utf-8")
        cmd = mmdc + ["-i", str(tmp), "-o", str(dst), "-c", str(HERE / "mermaid.json"),
                      "-b", "white", "-s", str(scale), "-q"]
        if no_sandbox:
            cmd += ["-p", str(HERE / "puppeteer-config.json")]
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            raise BuildError(f"mermaid-cli failed (exit {e.returncode}). On Linux, if Chromium reports "
                             f"'No usable sandbox', retry with --no-sandbox (see README, Troubleshooting).") from None
    if dst.suffix.lower() == ".svg":
        dst.write_text(inline_images(read_text(dst)), encoding="utf-8")
    if dst.suffix.lower() == ".svg" and "<foreignObject" in read_text(dst):
        raise BuildError(f"{dst} contains HTML labels (<foreignObject>), which Typst and many viewers "
                         f'cannot render. Keep "htmlLabels": false in mermaid.json.')


def collect(inputs):
    files = []
    for item in inputs:
        p = Path(item)
        files.extend(sorted(p.rglob("*.mmd")) if p.is_dir() else [p])
    if not files:
        raise BuildError("no .mmd files found")
    return files


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build Cisco-style network diagrams from Mermaid sources.")
    ap.add_argument("inputs", nargs="*", help=".mmd files or folders containing them")
    ap.add_argument("-o", "--output", help="output file (single input only)")
    ap.add_argument("-d", "--outdir", help="output folder (default: next to each input)")
    ap.add_argument("-f", "--format", choices=["svg", "png", "pdf"], default="svg",
                    help="output format when -o is not given (default: svg)")
    ap.add_argument("-s", "--scale", type=float, default=1.0, help="scale factor, useful for PNG (default: 1)")
    ap.add_argument("--no-sandbox", action="store_true",
                    default=os.environ.get("MMDC_NO_SANDBOX") == "1",
                    help="launch Chromium with --no-sandbox (Linux root/containers only; or set MMDC_NO_SANDBOX=1)")
    ap.add_argument("--list-icons", action="store_true", help="list available icons and exit")
    args = ap.parse_args(argv)

    try:
        if args.list_icons:
            print("\n".join(icon_names()))
            return 0
        if not args.inputs:
            ap.error("give at least one .mmd file or folder (or --list-icons)")
        files = collect(args.inputs)
        if args.output and len(files) != 1:
            ap.error("-o/--output needs exactly one input; use --outdir for several")
        mmdc = find_mmdc()
        for f in files:
            if args.output:
                dst = Path(args.output)
            else:
                dst = Path(args.outdir or f.parent) / f"{f.stem}.{args.format}"
            render(mmdc, f, dst.resolve(), args.scale, args.no_sandbox)
            print(f"wrote {dst}")
        return 0
    except BuildError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
