#!/usr/bin/env python3
"""Crawl the Living Neighbourhoods site into a reproducible local archive."""

from collections import deque
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.request import Request, urlopen


ROOT = "https://www.livingneighborhoods.org/"
OUTPUT = Path("archive/www.livingneighborhoods.org")
ALLOWED_HOSTS = {"www.livingneighborhoods.org", "livingneighborhoods.org"}


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key.lower() in {"href", "src", "data", "action"} and value:
                self.links.add(value)


def local_path(url):
    parsed = urlparse(url)
    path = parsed.path or "/index.html"
    if path.endswith("/"):
        path += "index.html"
    return OUTPUT / path.lstrip("/")


def same_site(url):
    return urlparse(url).hostname in ALLOWED_HOSTS


def normalize(base, raw):
    if not raw or raw.startswith(("#", "mailto:", "javascript:", "tel:")):
        return None
    absolute, _ = urldefrag(urljoin(base, raw))
    if urlparse(absolute).scheme not in {"http", "https"} or not same_site(absolute):
        return None
    return absolute


def links_from(content, content_type, base):
    text = content.decode("utf-8", errors="ignore")
    raw_links = set()
    if "html" in content_type:
        parser = LinkParser()
        parser.feed(text)
        raw_links.update(parser.links)
    if "css" in content_type:
        raw_links.update(re.findall(r"url\\(\\s*[\"']?([^\"')]+)", text))
    return {link for raw in raw_links if (link := normalize(base, raw))}


def fetch(url):
    request = Request(url, headers={"User-Agent": "livingneighborhoods-archive/1.0"})
    with urlopen(request, timeout=30) as response:
        return response.geturl(), response.headers.get_content_type(), response.read()


def main():
    queue = deque([ROOT, ROOT + "ht-0/bln-exp.htm"])
    seen = set()
    downloaded = 0
    failed = []
    OUTPUT.mkdir(parents=True, exist_ok=True)

    while queue:
        url = queue.popleft()
        if url in seen:
            continue
        seen.add(url)
        try:
            final_url, content_type, content = fetch(url)
            if not same_site(final_url):
                continue
            path = local_path(final_url)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            downloaded += 1
            queue.extend(links_from(content, content_type, final_url) - seen)
            print(f"[{downloaded}] {final_url} -> {path}")
        except Exception as error:  # keep the crawl going and report gaps at end
            failed.append((url, str(error)))
            print(f"FAILED {url}: {error}", file=sys.stderr)

    (OUTPUT / "ARCHIVE-METADATA.txt").write_text(
        "Source: https://www.livingneighborhoods.org/\n"
        "Crawled: 2026-08-21\n"
        f"URLs visited: {len(seen)}\n"
        f"Files downloaded: {downloaded}\n"
        f"Failed URLs: {len(failed)}\n"
        + "\n".join(f"FAILED {url}: {error}" for url, error in failed)
        + "\n",
        encoding="utf-8",
    )
    if failed:
        print(f"Completed with {len(failed)} failed URL(s).", file=sys.stderr)


if __name__ == "__main__":
    main()
