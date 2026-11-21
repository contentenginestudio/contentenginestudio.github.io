#!/usr/bin/env python3
"""Fill the {{...}} placeholders in this site with real values.

Example:
  python3 fill.py --studio "Content Engine" --email "hello@example.com" \
      --base-url "https://example.github.io/content-site" \
      --handles scale=ScaleOfWhat survive=SurviveTheDays torah=TorahUnrolled \
                lantern=TheBronzeLantern ranked=ClearlyRanked

Edits the files in place (undo with `git checkout -- .`). Use --out DIR to write a filled
copy somewhere else instead. Uses only the Python standard library.
"""
from __future__ import annotations

import argparse
import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGETS = ["index.html", "privacy.html", "terms.html", "404.html", "robots.txt", "sitemap.xml"]
COPY_SKIP = {".git", "_preview", "__pycache__", ".DS_Store"}

# Defaults come from the channel kits (content-engine/assets/channels/*/kit.json).
DEFAULT_HANDLES = {
    "scale": "ScaleOfWhat",
    "survive": "SurviveTheDays",
    "torah": "TorahUnrolled",
    "lantern": "TheBronzeLantern",
    "ranked": "ClearlyRanked",
}
TOKEN_RE = re.compile(r"\{\{[A-Za-z_]+\}\}")


def parse_args(argv):
    p = argparse.ArgumentParser(description="Fill the site's {{...}} placeholders.")
    p.add_argument("--studio", default="Content Engine", help='studio name (default: "Content Engine")')
    p.add_argument("--email", required=True, help="public contact email")
    p.add_argument("--base-url", required=True,
                   help="site root URL, e.g. https://user.github.io/content-site or https://example.com")
    p.add_argument("--handles", nargs="*", default=[], metavar="KEY=HANDLE",
                   help="YouTube handles without @; keys: " + ", ".join(DEFAULT_HANDLES))
    p.add_argument("--cname", metavar="DOMAIN", help="also write a CNAME file for a custom domain")
    p.add_argument("--out", metavar="DIR", help="write a filled copy to DIR instead of editing in place")
    return p.parse_args(argv)


def build_values(a) -> dict[str, str]:
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", a.email):
        sys.exit(f"error: --email {a.email!r} doesn't look like an email address")
    base = a.base_url.strip().rstrip("/")
    if not re.fullmatch(r"https://[A-Za-z0-9.-]+(:\d+)?(/[A-Za-z0-9._~/-]*)?", base):
        sys.exit(f"error: --base-url must be an https:// URL, got {a.base_url!r}")
    handles = dict(DEFAULT_HANDLES)
    for item in a.handles:
        key, sep, val = item.partition("=")
        if not sep or key not in DEFAULT_HANDLES:
            sys.exit(f"error: bad --handles item {item!r}; use KEY=HANDLE with KEY in {', '.join(DEFAULT_HANDLES)}")
        val = val.strip().lstrip("@")
        if not re.fullmatch(r"[A-Za-z0-9._-]{3,30}", val):
            sys.exit(f"error: {val!r} is not a valid YouTube handle")
        handles[key] = val
    if not a.studio.strip():
        sys.exit("error: --studio can't be empty")
    values = {"STUDIO_NAME": a.studio.strip(), "CONTACT_EMAIL": a.email.strip(), "BASE_URL": base}
    values.update({f"HANDLE_{k}": v for k, v in handles.items()})
    return values


def fill_text(text: str, values: dict[str, str], escape: bool) -> str:
    for key, val in values.items():
        text = text.replace("{{" + key + "}}", html.escape(val, quote=True) if escape else val)
    return text


def main(argv=None) -> int:
    a = parse_args(argv if argv is not None else sys.argv[1:])
    values = build_values(a)
    dest = ROOT
    if a.out:
        dest = Path(a.out).resolve()
        preview = ROOT / "_preview"
        if dest == ROOT or (ROOT in dest.parents and preview not in dest.parents):
            sys.exit("error: --out must be outside this folder, or inside _preview/")
        if dest.exists():
            if preview not in dest.parents and any(dest.iterdir()):
                sys.exit(f"error: {dest} already exists and is not empty")
            shutil.rmtree(dest)
        shutil.copytree(ROOT, dest, ignore=lambda d, names: [n for n in names if n in COPY_SKIP])

    leftovers = []
    for name in TARGETS:
        path = dest / name
        text = path.read_text(encoding="utf-8")
        # Every value is escaped for HTML/XML; robots.txt is plain text and only gets the URL.
        new = fill_text(text, values, escape=name != "robots.txt")
        path.write_text(new, encoding="utf-8")
        leftovers += [f"{name}: {t}" for t in sorted(set(TOKEN_RE.findall(new)))]

    if a.cname:
        domain = a.cname.strip().lower()
        if not re.fullmatch(r"[a-z0-9-]+(\.[a-z0-9-]+)+", domain):
            sys.exit(f"error: --cname {a.cname!r} is not a domain name")
        (dest / "CNAME").write_text(domain + "\n", encoding="utf-8")

    print(f"Filled {len(TARGETS)} files in {dest}")
    for k, v in values.items():
        print(f"  {{{{{k}}}}} -> {v}")
    if leftovers:
        print("warning: placeholders still present:\n  " + "\n  ".join(leftovers))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
