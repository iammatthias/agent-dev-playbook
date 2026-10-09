#!/usr/bin/env python3
"""Diff claude.dev's sitemap against the posts already in the corpus.

Usage:
  check_sitemap.py check  <seen.txt> <out_dir>   # write new posts' markdown to out_dir, print their URLs
  check_sitemap.py record <seen.txt> <out_dir>   # append the URLs fetched into out_dir to seen.txt
"""
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

SITEMAP = "https://claude.dev/sitemap.xml"
POST_RE = re.compile(r"^https://claude\.dev/blog/[^/]+/$")
NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
UA = {"User-Agent": "agent-dev-playbook-refresh"}


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read()


def normalize(url):
    url = url.strip()
    return url if url.endswith("/") else url + "/"


def sitemap_entries(url, depth=0):
    """Yield (loc, lastmod) pairs, following sitemap indexes."""
    root = ET.fromstring(fetch(url))
    if root.tag == NS + "sitemapindex" and depth < 3:
        for sm in root.iter(NS + "sitemap"):
            yield from sitemap_entries(sm.findtext(NS + "loc").strip(), depth + 1)
        return
    for u in root.iter(NS + "url"):
        yield normalize(u.findtext(NS + "loc")), (u.findtext(NS + "lastmod") or "").strip()


def check(seen_path, out_dir):
    seen = {normalize(l) for l in seen_path.read_text().splitlines() if l.strip()}
    new = sorted({(loc, mod) for loc, mod in sitemap_entries(SITEMAP)
                  if POST_RE.match(loc) and loc not in seen})
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for loc, mod in new:
        slug = loc.rstrip("/").rsplit("/", 1)[1]
        # Posts serve clean markdown at <url-without-trailing-slash>.md
        (out_dir / f"{slug}.md").write_bytes(fetch(loc.rstrip("/") + ".md"))
        manifest.append({"url": loc, "lastmod": mod, "file": f"{slug}.md"})
        print(loc)
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))


def record(seen_path, out_dir):
    manifest = json.loads((out_dir / "manifest.json").read_text())
    seen = [l for l in seen_path.read_text().splitlines() if l.strip()]
    seen += [m["url"] for m in manifest if m["url"] not in seen]
    seen_path.write_text("\n".join(sorted(set(seen))) + "\n")


if __name__ == "__main__":
    cmd, seen_path, out_dir = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    {"check": check, "record": record}[cmd](seen_path, out_dir)
