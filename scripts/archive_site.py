#!/usr/bin/env python3
"""Crawl Living Neighbourhoods into a reproducible, checksummed archive."""

from collections import deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError
from urllib.parse import quote, unquote, urldefrag, urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen


ROOT = "https://www.livingneighborhoods.org/"
OUTPUT = Path("archive/www.livingneighborhoods.org")
MANIFEST = OUTPUT / "manifest.json"
ALLOWED_HOSTS = {"www.livingneighborhoods.org", "livingneighborhoods.org"}
START_URLS = (
    ROOT,
    ROOT + "ht-0/bln-exp.htm",
    ROOT + "ht-0/menu-exp.htm",
)
MAX_WORKERS = 6
RETRIES = 3

FILE_EXTENSIONS = (
    "htm|html|css|js|pdf|txt|xml|jpe?g|gif|png|webp|svg|ico|"
    "zip|doc|docx|xls|xlsx|ppt|pptx|mov|mp4|avi|wav|mp3|swf|class|jar"
)
ALLOWED_SUFFIXES = {
    ".htm", ".html", ".css", ".js", ".pdf", ".txt", ".xml",
    ".jpg", ".jpeg", ".gif", ".png", ".webp", ".svg", ".ico",
    ".zip", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".mov", ".mp4", ".avi", ".wav", ".mp3", ".swf", ".class", ".jar",
}
FILE_REFERENCE_RE = re.compile(
    rf"(?i)(?:https?://(?:www\.)?livingneighborhoods\.org)?"
    rf"(?:\.\.?/|/)?[a-z0-9_@%+~./-]+\.(?:{FILE_EXTENSIONS})"
    rf"(?:\?[^\s\"'<>)]*)?(?=$|[\s\"'<>),;#])"
)
CSS_URL_RE = re.compile(r"url\(\s*[\"']?([^\"')]+)", re.IGNORECASE)


class LinkParser(HTMLParser):
    """Collect every attribute value; legacy pages hide URLs in event handlers."""

    def __init__(self):
        super().__init__()
        self.values = set()

    def handle_starttag(self, tag, attrs):
        del tag
        self.values.update(value for _, value in attrs if value)


def local_path(url):
    parsed = urlparse(url)
    path = unquote(parsed.path) or "/index.html"
    if path.endswith("/"):
        path += "index.html"
    return OUTPUT / path.lstrip("/")


def same_site(url):
    return urlparse(url).hostname in ALLOWED_HOSTS


def normalize(base, raw):
    """Return one canonical same-site static URL or None."""
    if not raw:
        return None
    raw = unescape(raw).replace("\\", "/").strip().strip("\"'")
    if raw.lower().startswith(("#", "mailto:", "javascript:", "tel:", "data:")):
        return None
    absolute, _ = urldefrag(urljoin(base, raw))
    parsed = urlparse(absolute)
    if parsed.scheme not in {"http", "https"} or parsed.hostname not in ALLOWED_HOSTS:
        return None
    if parsed.path.startswith("/cgi-bin/"):
        return None
    suffix = Path(parsed.path).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES and not parsed.path.endswith("/"):
        return None
    path = quote(unquote(parsed.path or "/"), safe="/:@-._~%+")
    return urlunparse(("https", "www.livingneighborhoods.org", path, "", "", ""))


def links_from(content, content_type, base):
    """Extract ordinary and legacy-scripted same-site references."""
    text = content.decode("latin-1", errors="ignore")
    path_text = text.replace("\\", "/")
    raw_links = set(FILE_REFERENCE_RE.findall(path_text))

    if "html" in content_type:
        parser = LinkParser()
        parser.feed(text)
        for value in parser.values:
            raw_links.update(FILE_REFERENCE_RE.findall(value))
            if not value.lower().startswith(("javascript:", "mailto:", "tel:", "data:")):
                raw_links.add(value)

    if "css" in content_type:
        raw_links.update(CSS_URL_RE.findall(text))

    return {link for raw in raw_links if (link := normalize(base, raw))}


def fetch(url, cached=None):
    """Fetch one URL with bounded retries and return a manifest-shaped result."""
    if cached:
        cached_path = cached.get("local_path")
        if cached_path and Path(cached_path).is_file():
            return {
                "url": url,
                "final_url": cached["final_url"],
                "status": cached["status"],
                "content_type": cached["content_type"],
                "content": Path(cached_path).read_bytes(),
                "error": None,
            }
        if isinstance(cached.get("status"), int) and 400 <= cached["status"] < 500:
            return {
                "url": url,
                "final_url": cached.get("final_url", url),
                "status": cached["status"],
                "content_type": cached.get("content_type"),
                "content": b"",
                "error": cached.get("error"),
            }
    error = None
    for attempt in range(RETRIES):
        try:
            request = Request(url, headers={"User-Agent": "livingneighborhoods-archive/2.0"})
            with urlopen(request, timeout=30) as response:
                content = response.read()
                return {
                    "url": url,
                    "final_url": normalize(ROOT, response.geturl()) or response.geturl(),
                    "status": response.status,
                    "content_type": response.headers.get_content_type(),
                    "content": content,
                    "error": None,
                }
        except HTTPError as exc:
            return {
                "url": url,
                "final_url": url,
                "status": exc.code,
                "content_type": exc.headers.get_content_type() if exc.headers else None,
                "content": b"",
                "error": str(exc),
            }
        except Exception as exc:  # transient network errors are retried
            error = str(exc)
            if attempt + 1 < RETRIES:
                time.sleep(0.5 * (attempt + 1))
    return {
        "url": url,
        "final_url": url,
        "status": None,
        "content_type": None,
        "content": b"",
        "error": error,
    }


def crawl():
    queue = deque((url, None) for url in START_URLS)
    scheduled = set()
    records = []
    cache = {}
    if MANIFEST.is_file():
        previous = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cache = {record["url"]: record for record in previous.get("records", [])}
    OUTPUT.mkdir(parents=True, exist_ok=True)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        while queue:
            batch = []
            while queue and len(batch) < MAX_WORKERS * 2:
                url, discovered_from = queue.popleft()
                if url in scheduled:
                    continue
                scheduled.add(url)
                batch.append((url, discovered_from))

            if not batch:
                continue

            results = executor.map(
                lambda item: fetch(item[0], cache.get(item[0])),
                batch,
            )
            for result, (_, discovered_from) in zip(results, batch):
                content = result.pop("content")
                record = {
                    **result,
                    "discovered_from": discovered_from,
                    "bytes": len(content),
                    "sha256": sha256(content).hexdigest() if content else None,
                    "local_path": None,
                }

                if result["status"] in {200, 206} and content and same_site(result["final_url"]):
                    path = local_path(result["final_url"])
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(content)
                    record["local_path"] = path.as_posix()
                    for link in links_from(content, result["content_type"] or "", result["final_url"]):
                        if link not in scheduled:
                            queue.append((link, result["url"]))
                    print(f"[{len(records) + 1}] {result['final_url']} -> {path}")
                else:
                    print(f"FAILED {result['url']}: {result['status'] or result['error']}")
                records.append(record)

    return sorted(records, key=lambda record: record["url"])


def is_html_record(record):
    return bool(record.get("local_path")) and "html" in (record.get("content_type") or "")


def write_reports(records):
    crawled_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    successful = [record for record in records if record["local_path"]]
    failures = [record for record in records if not record["local_path"]]
    html_files = [record for record in successful if is_html_record(record)]
    manifest = {
        "source": ROOT,
        "crawled_at": crawled_at,
        "scope": "All static same-site resources reachable from the homepage, legacy menu, and recursive page/resource references.",
        "records": records,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    lines = [
        f"Source: {ROOT}",
        f"Crawled: {crawled_at}",
        f"URLs visited: {len(records)}",
        f"Files downloaded: {len(successful)}",
        f"HTML pages downloaded: {len(html_files)}",
        f"Bytes downloaded: {sum(record['bytes'] for record in successful)}",
        f"Failed URLs: {len(failures)}",
        "Scope: all static same-site resources reachable from the homepage, legacy menu, and recursive references.",
        "Note: the source provides no sitemap; unlinked or externally linked files cannot be proven absent.",
    ]
    lines.extend(
        f"FAILED {record['url']}: {record['status'] or record['error']}" for record in failures
    )
    (OUTPUT / "ARCHIVE-METADATA.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    records = crawl()
    write_reports(records)
    successful = sum(bool(record["local_path"]) for record in records)
    failures = len(records) - successful
    print(f"Archived {successful} resources; {failures} failed URLs recorded in {MANIFEST}.")


if __name__ == "__main__":
    main()
