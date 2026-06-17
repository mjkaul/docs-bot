#!/usr/bin/env python3
"""Publish the enriched corpus to a Confluence Cloud space (REST API v2).

- Mirrors the section hierarchy as a page tree (sections -> parent pages).
- Renders a metadata panel (topic type, subjects, terms) at the top of each page,
  so the taxonomy/graph layer is visible in Confluence.
- Idempotent: pages are matched by title within the space and updated in place.
- CC-BY attribution footer on every page.

Usage:
  python3 scripts/publish_confluence.py --dry-run          # plan only
  python3 scripts/publish_confluence.py                    # publish everything
  python3 scripts/publish_confluence.py --limit 20         # first 20 topics (smoke test)

Needs .env: CONFLUENCE_BASE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, CONFLUENCE_SPACE_KEY
Free plan note: stay polite with the API; this script throttles to ~2 req/s.
"""
import argparse
import sys
import time
from pathlib import Path

import frontmatter
import markdown
import requests
from dotenv import load_dotenv
import os

ROOT = Path(__file__).resolve().parent.parent
ENRICHED = ROOT / "content" / "enriched"


def storage_body(post) -> str:
    """Markdown -> Confluence storage format (XHTML) with metadata panel + attribution."""
    html = markdown.markdown(post.content, extensions=["tables", "fenced_code"])
    # Confluence storage format is XHTML-ish; python-markdown output is close enough
    # for text/tables/code. Fenced code blocks become <pre><code> which renders fine.
    subjects = ", ".join(post.get("subjects") or []) or "—"
    terms = ", ".join(post.get("mentions") or []) or "—"
    panel = (
        '<table><tbody>'
        f'<tr><th>Topic type</th><td>{post["topic_type"]}</td></tr>'
        f'<tr><th>Subjects</th><td>{subjects}</td></tr>'
        f'<tr><th>Terms</th><td>{terms}</td></tr>'
        f'<tr><th>Topic ID</th><td>{post["id"]}</td></tr>'
        '</tbody></table>'
    )
    footer = (
        f'<hr/><p><em>Source: <a href="{post["source"]}">kubernetes/website</a> '
        '&copy; The Kubernetes Authors, CC-BY 4.0. Modified (metadata enrichment, '
        'shortcode removal) by docs_bot.</em></p>'
    )
    return panel + html + footer


class Confluence:
    def __init__(self):
        load_dotenv(ROOT / ".env")
        self.base = os.environ["CONFLUENCE_BASE_URL"].rstrip("/") + "/wiki/api/v2"
        self.auth = (os.environ["CONFLUENCE_EMAIL"], os.environ["CONFLUENCE_API_TOKEN"])
        self.space_key = os.environ["CONFLUENCE_SPACE_KEY"]
        self.s = requests.Session()
        self.s.auth = self.auth
        self.s.headers["Content-Type"] = "application/json"

    def _req(self, method, path, **kw):
        time.sleep(0.5)  # be polite on the free plan
        r = self.s.request(method, self.base + path, **kw)
        if r.status_code >= 400:
            sys.exit(f"Confluence API {r.status_code} on {method} {path}: {r.text[:500]}")
        return r.json() if r.text else {}

    def space_id(self) -> str:
        res = self._req("GET", f"/spaces?keys={self.space_key}")
        if not res.get("results"):
            sys.exit(f"Space '{self.space_key}' not found — create it in Confluence first.")
        return res["results"][0]["id"]

    def find_page(self, space_id: str, title: str):
        res = self._req("GET", f"/spaces/{space_id}/pages",
                        params={"title": title, "limit": 1})
        return res["results"][0] if res.get("results") else None

    def upsert(self, space_id: str, title: str, body: str, parent_id=None) -> str:
        existing = self.find_page(space_id, title)
        payload = {
            "spaceId": space_id, "status": "current", "title": title,
            "body": {"representation": "storage", "value": body},
        }
        if parent_id:
            payload["parentId"] = parent_id
        if existing:
            page = self._req("GET", f"/pages/{existing['id']}")
            payload["id"] = existing["id"]
            payload["version"] = {"number": page["version"]["number"] + 1}
            self._req("PUT", f"/pages/{existing['id']}", json=payload)
            return existing["id"]
        return self._req("POST", "/pages", json=payload)["id"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    posts = [frontmatter.load(f) for f in sorted(ENRICHED.rglob("*.md"))]
    # Publish shallow-first so parents exist before children.
    posts.sort(key=lambda p: p["id"].count("."))
    if args.limit:
        posts = posts[: args.limit]

    # Disambiguate duplicate titles (Confluence titles are unique per space).
    seen, titles = {}, {}
    for p in posts:
        t = p["title"]
        seen[t] = seen.get(t, 0) + 1
        titles[p["id"]] = t if seen[t] == 1 else f"{t} ({p['id']})"

    if args.dry_run:
        for p in posts:
            indent = "  " * p["id"].count(".")
            print(f"{indent}{titles[p['id']]}  [{p['topic_type']}]")
        print(f"\n{len(posts)} pages would be published.")
        return

    api = Confluence()
    space_id = api.space_id()
    page_ids: dict[str, str] = {}
    for i, p in enumerate(posts, 1):
        parent_id = None
        parts = p["id"].split(".")
        for j in range(len(parts) - 1, 0, -1):
            pid = ".".join(parts[:j])
            if pid in page_ids:
                parent_id = page_ids[pid]
                break
        page_ids[p["id"]] = api.upsert(space_id, titles[p["id"]], storage_body(p), parent_id)
        print(f"[{i}/{len(posts)}] {titles[p['id']]}")
    print(">> Done.")


if __name__ == "__main__":
    main()
