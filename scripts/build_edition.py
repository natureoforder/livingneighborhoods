#!/usr/bin/env python3
"""Build the reader edition in edition/ from the archived HTML, following scripts/edition_map.py.

For each edition page: decode the archived HTML, strip scripts/styles/comments, parse with pandoc
to its JSON AST, clean the AST (unwrap layout tables, drop legacy navigation and boilerplate,
turn shouty labels into headings, rewrite links and images to edition routes), and write GitHub
Markdown with provenance frontmatter. Merged sources become extra sections.

Pages whose frontmatter contains `edited: true` are hand-edited and are never overwritten; the
build only reports when their source checksum no longer matches.

Referenced images and every PDF are copied byte-for-byte to edition/assets/<archive path>.
Writes edition/_build/links.json (dead or unmapped links) for the review queue.
"""

from html import unescape
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from edition_map import MAP, P, M, D, X  # noqa: E402
from edition_titles import TITLES  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "archive/www.livingneighborhoods.org"
EDITION = ROOT / "edition"
ASSETS = "assets"
BASE = "https://www.livingneighborhoods.org/"
ASSET_EXT = {".jpg", ".jpeg", ".gif", ".png", ".bmp", ".pdf"}
SPACER_MAX_BYTES = 200  # tiny gifs used as spacers

BOILERPLATE = [
    r"^a fragment of the generative code for neighbou?rhoods\.?$",
    r"^fragment of the generative code for neighbou?rhoods\.?$",
    r"^©.*\bCES\b.*$", r"^copyright\b.*$", r"^terms of use.*$",
    r"^text coming$", r"^back to\b.*$", r"^go back$", r"^back$", r"^top$", r"^menu$",
    r"^jump to action$", r"^we recommend using.*$", r"^print this page$",
    r"^back to (top level|neighborhood list|countries menu).*$",
]
BOILER_RE = [re.compile(p, re.I) for p in BOILERPLATE]


# ---------------------------------------------------------------- helpers

def read_html(path):
    data = path.read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = data.decode("cp1252", errors="replace")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"<(script|style|noscript)\b.*?</\1\s*>", "", text, flags=re.S | re.I)
    text = re.sub(r"<(script|style)\b[^>]*/?>", "", text, flags=re.I)
    # CSS rules that leaked into body text on some pages
    text = re.sub(r"\.[a-z0-9_-]+\s*\{[^}]*\}", "", text, flags=re.I)
    return text


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stringify(inlines):
    out = []
    for el in inlines:
        t = el.get("t")
        c = el.get("c")
        if t == "Str":
            out.append(c)
        elif t in ("Space", "SoftBreak", "LineBreak"):
            out.append(" ")
        elif t in ("Emph", "Strong", "Underline", "SmallCaps", "Strikeout", "Superscript", "Subscript"):
            out.append(stringify(c))
        elif t in ("Link", "Span"):
            out.append(stringify(c[1]))
        elif t == "Quoted":
            out.append('"' + stringify(c[1]) + '"')
        elif t == "Code":
            out.append(c[1])
    return "".join(out)


def is_boiler(text):
    text = re.sub(r"\s+", " ", text).strip("  |:-")
    if not text:
        return True
    return any(r.match(text) for r in BOILER_RE)


def sentence_case(text):
    text = text.strip()
    if not text:
        return text
    words = text.split()
    keep = {"I", "CES", "GPS", "UK", "USA", "US", "II", "III", "IV"}
    out = []
    for i, w in enumerate(words):
        core = re.sub(r"[^A-Za-z]", "", w)
        if core in keep:
            out.append(w)
        elif i == 0:
            out.append(w[:1].upper() + w[1:].lower())
        else:
            out.append(w.lower())
    return " ".join(out)


def is_shouty(text):
    letters = re.sub(r"[^A-Za-z]", "", text)
    return len(letters) >= 3 and letters.isupper()


def rel(from_dest, to_path):
    """Relative URL from edition page `from_dest` (no .md) to edition path `to_path`."""
    start = PurePosixPath(from_dest).parent
    return os.path.relpath(to_path, start or ".").replace(os.sep, "/")


# ---------------------------------------------------------------- link resolution

class Resolver:
    def __init__(self):
        self.dest_of = {}
        for src, (role, dest, _) in MAP.items():
            if role != X:
                self.dest_of[src] = dest
        self.assets = set()
        self.dead = []

    def archive_target(self, page_src, url):
        parts = urlsplit(url)
        if parts.scheme in ("http", "https"):
            if parts.netloc.lower().endswith("livingneighborhoods.org"):
                path = parts.path.lstrip("/")
            else:
                return None, url
        elif parts.scheme in ("ftp",):
            return None, url
        elif parts.scheme:
            return None, None  # file:, javascript: leftovers and the like
        else:
            if not parts.path:
                return None, None
            path = str(PurePosixPath(page_src).parent / unquote(parts.path))
        path = os.path.normpath(path).replace(os.sep, "/").lstrip("./")
        return path, parts.fragment

    def link(self, page_src, page_dest, url):
        """Return new URL, or None to unlink."""
        if url.startswith(("mailto:", "#")):
            return url
        if url.lower().startswith("javascript:"):
            m = re.search(r"['\"]([^'\"]+\.s?html?)['\"]", url)
            if not m:
                return None
            url = m.group(1)
        path, frag = self.archive_target(page_src, url)
        if path is None:
            return frag  # external URL (or None)
        if path.endswith(".shtml"):
            path = path[:-6] + ".htm"
        if path in self.dest_of:
            return rel(page_dest, self.dest_of[path] + ".md")
        if (ARCHIVE / path).is_file() and PurePosixPath(path).suffix.lower() in ASSET_EXT:
            self.assets.add(path)
            return rel(page_dest, f"{ASSETS}/{path}")
        self.dead.append({"page": page_dest, "source": page_src, "href": url, "resolved": path})
        return None

    def image(self, page_src, page_dest, url):
        path, _ = self.archive_target(page_src, url)
        if path is None or not (ARCHIVE / path).is_file():
            if path is not None:
                self.dead.append({"page": page_dest, "source": page_src, "img": url, "resolved": path})
            return None
        if (ARCHIVE / path).stat().st_size <= SPACER_MAX_BYTES:
            return None
        self.assets.add(path)
        return rel(page_dest, f"{ASSETS}/{path}")


# ---------------------------------------------------------------- AST cleaning

def table_blocks(table):
    _, attr, caption, colspecs, head, bodies, foot = [None] + table["c"]
    blocks = []
    rows = list(head[1])
    for body in bodies:
        rows += body[2] + body[3]
    rows += foot[1]
    for row in rows:
        for cell in row[1]:
            blocks.extend(cell[4])
    return blocks


class Cleaner:
    def __init__(self, resolver, src, dest):
        self.r = resolver
        self.src = src
        self.dest = dest

    def inlines(self, items):
        out = []
        for el in items:
            t = el.get("t")
            c = el.get("c")
            if t == "Image":
                attr, alt, (url, title) = c
                new = self.r.image(self.src, self.dest, url)
                if new:
                    alt_text = stringify(alt).strip()
                    out.append({"t": "Image", "c": [["", [], []], [{"t": "Str", "c": alt_text}] if alt_text else [], [new, ""]]})
            elif t == "Link":
                attr, text, (url, title) = c
                text = self.inlines(text)
                if is_boiler(stringify(text)) and re.match(r"(?i)\s*(back|go back|top|menu)", stringify(text)):
                    continue
                new = self.r.link(self.src, self.dest, url)
                if new:
                    out.append({"t": "Link", "c": [["", [], []], text, [new, ""]]})
                else:
                    out.extend(text)
            elif t in ("Span",):
                out.extend(self.inlines(c[1]))
            elif t in ("Emph", "Strong", "Underline", "SmallCaps", "Strikeout", "Superscript", "Subscript"):
                inner = self.inlines(c)
                if stringify(inner).strip():
                    out.append({"t": "Emph" if t == "Underline" else t, "c": inner})
                else:
                    out.extend(i for i in inner if i.get("t") in ("Space", "Image"))
            elif t == "Quoted":
                out.append({"t": t, "c": [c[0], self.inlines(c[1])]})
            elif t in ("RawInline", "Note"):
                continue
            else:
                out.append(el)
        return trim(out)

    def blocks(self, items):
        out = []
        for b in items:
            t = b.get("t")
            c = b.get("c")
            if t == "Table":
                out.extend(self.blocks(table_blocks(b)))
            elif t in ("Div",):
                out.extend(self.blocks(c[1]))
            elif t == "Figure":
                out.extend(self.blocks(c[2]))
            elif t in ("Para", "Plain"):
                inl = self.inlines(c)
                out.extend(self.para(inl))
            elif t == "Header":
                inl = self.inlines(c[2])
                text = stringify(inl).strip()
                if is_boiler(text):
                    continue
                if is_shouty(text):
                    inl = [{"t": "Str", "c": sentence_case(text)}]
                out.append({"t": "Header", "c": [max(2, c[0]), ["", [], []], inl]})
            elif t == "BulletList":
                items2 = [self.blocks(i) for i in c]
                items2 = [i for i in items2 if i]
                if items2:
                    out.append({"t": "BulletList", "c": items2})
            elif t == "OrderedList":
                items2 = [self.blocks(i) for i in c[1]]
                items2 = [i for i in items2 if i]
                if items2:
                    out.append({"t": "OrderedList", "c": [c[0], items2]})
            elif t == "BlockQuote":
                inner = self.blocks(c)
                if inner:
                    # old pages used blockquote purely for indentation
                    out.extend(inner)
            elif t == "LineBlock":
                for line in c:
                    out.extend(self.para(self.inlines(line)))
            elif t in ("HorizontalRule", "RawBlock", "Null"):
                continue
            elif t == "DefinitionList":
                for term, defs in c:
                    out.extend(self.para(self.inlines(term)))
                    for d in defs:
                        out.extend(self.blocks(d))
            else:
                out.append(b)
        return out

    def para(self, inl):
        """Split a paragraph on line breaks, drop boilerplate lines, promote shouty labels."""
        lines, cur = [], []
        for el in inl:
            if el.get("t") == "LineBreak":
                lines.append(cur)
                cur = []
            else:
                cur.append(el)
        lines.append(cur)
        out = []
        body = []
        for line in lines:
            line = trim(line)
            text = stringify(line).strip()
            images = [e for e in line if e.get("t") == "Image"]
            if not text and not images:
                continue
            if text and is_boiler(text) and not images:
                continue
            words = text.split()
            if text and not images and is_shouty(text) and len(words) <= 8:
                if body:
                    out.append({"t": "Para", "c": join_lines(body)})
                    body = []
                out.append({"t": "Header", "c": [2, ["", [], []], [{"t": "Str", "c": sentence_case(text.rstrip(":. "))}]]})
                continue
            if images and not text:
                if body:
                    out.append({"t": "Para", "c": join_lines(body)})
                    body = []
                for img in images:
                    out.append({"t": "Para", "c": [img]})
                continue
            body.append(line)
        if body:
            out.append({"t": "Para", "c": join_lines(body)})
        return out


def trim(inl):
    while inl and inl[0].get("t") in ("Space", "SoftBreak", "LineBreak"):
        inl = inl[1:]
    while inl and inl[-1].get("t") in ("Space", "SoftBreak", "LineBreak"):
        inl = inl[:-1]
    return inl


def join_lines(lines):
    out = []
    for i, line in enumerate(lines):
        if i:
            out.append({"t": "Space"})
        out.extend(line)
    return out


def dedupe_headers(blocks):
    """Drop consecutive duplicate headers and headers with nothing under them before the next header."""
    out = []
    for b in blocks:
        if b["t"] == "Header" and out and out[-1]["t"] == "Header":
            if stringify(out[-1]["c"][2]).lower() == stringify(b["c"][2]).lower():
                continue
        out.append(b)
    while out and out[-1]["t"] == "Header":
        out.pop()
    return out


def to_markdown(blocks):
    doc = {"pandoc-api-version": API, "meta": {}, "blocks": blocks}
    md = subprocess.run(
        ["pandoc", "-f", "json", "-t", "gfm-raw_html", "--wrap=none"],
        input=json.dumps(doc), check=True, capture_output=True, text=True,
    ).stdout
    md = re.sub(r"\n{3,}", "\n\n", md)
    md = re.sub(r"(?m)^\\$\n?", "", md)
    md = md.replace(" ", " ")
    # lower-case shouty lead-ins at the start of a paragraph: "IF ONE THING, MORE THAN ANY OTHER, distinguishes"
    def fix(m):
        return sentence_case(m.group(1)) + m.group(2)
    md = re.sub(r"(?m)^((?:[A-Z][A-Z'’,\-]*\s+){2,}[A-Z][A-Z'’,\-]*)(\s+[a-z])", fix, md)
    # whole shouty paragraphs (not headings, lists or images)
    def calm(m):
        line = m.group(0)
        return sentence_case(line) if is_shouty(line) and len(line.split()) > 8 else line
    md = re.sub(r"(?m)^(?![#!|*\-\[]).+$", calm, md)
    return md.strip() + "\n"


def parse(path):
    html = read_html(path)
    out = subprocess.run(
        ["pandoc", "-f", "html-native_divs-native_spans", "-t", "json"],
        input=html, check=True, capture_output=True, text=True,
    ).stdout
    doc = json.loads(out)
    global API
    API = doc["pandoc-api-version"]
    return doc["blocks"], html


API = [1, 23, 1, 1]


# ---------------------------------------------------------------- titles and frontmatter

def html_title(html):
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    return re.sub(r"\s+", " ", unescape(m.group(1))).strip() if m else ""


def clean_title(raw, dest):
    if dest in TITLES:
        return TITLES[dest]
    t = re.split(r"\s+--\s*|\s+-\s+", raw)[-1].strip() if raw else ""
    if not t or len(t) < 3:
        t = PurePosixPath(dest).name.replace("-", " ")
    if is_shouty(t):
        t = sentence_case(t)
    return t[:1].upper() + t[1:]


def description(md):
    for para in md.split("\n\n"):
        p = para.strip()
        if not p or p.startswith(("#", "!", "-", "*", "|", "<")) or len(p) < 60:
            continue
        p = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", p)
        p = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", p)
        p = re.sub(r"[*_`]", "", p).strip()
        m = re.match(r"(.{40,200}?[.!?])(\s|$)", p)
        return (m.group(1) if m else p[:157].rsplit(" ", 1)[0] + "…")
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)|\[([^\]]*)\]\([^)]*\)|[#*_`>|-]", lambda m: m.group(1) or "", md)
    text = " ".join(text.split())
    return text[:157].rsplit(" ", 1)[0] + "…" if len(text) > 157 else text


def q(v):
    return json.dumps(v, ensure_ascii=False)


def frontmatter(fields):
    lines = ["---"]
    for k, v in fields.items():
        if v is None or v == "" or v == []:
            continue
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                if isinstance(item, dict):
                    first = True
                    for ik, iv in item.items():
                        lines.append(f"  {'- ' if first else '  '}{ik}: {q(iv)}")
                        first = False
                else:
                    lines.append(f"  - {q(item)}")
        else:
            lines.append(f"{k}: {q(v)}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def read_front(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    head, _, body = text[3:].partition("\n---")
    front = {}
    for line in head.splitlines():
        m = re.match(r"^([a-z0-9_]+):\s*(.*)$", line)
        if m:
            front[m.group(1)] = m.group(2).strip()
    return front, body


# ---------------------------------------------------------------- navigation

def step_order():
    """Ordered step lists per generative-code phase, from map order."""
    phases = {}
    for src, (role, dest, _) in MAP.items():
        if role == P and dest.startswith("generative-code/") and dest.count("/") == 2 and not dest.endswith("/index"):
            phases.setdefault(dest.rsplit("/", 1)[0], []).append(dest)
    return phases


# ---------------------------------------------------------------- main

CREDIT = ("*From* Building Living Neighborhoods *by Christopher Alexander, Maggie Moore Alexander, Randy Schmidt and "
          "Nick Littlestone, with Bev Behrman and Howard Davis. © Center for Environmental Structure. "
          "[Original page]({source}).*")


def build():
    resolver = Resolver()
    groups = {}
    for src, (role, dest, note) in MAP.items():
        if role in (P, M):
            groups.setdefault(dest, []).append((role, src, note))
    phases = step_order()
    titles = {}
    report = {"written": 0, "kept_edited": [], "stale_edited": []}

    for dest, members in groups.items():
        members.sort(key=lambda m: m[0] != P)  # canonical first
        out_path = EDITION / f"{dest}.md"
        role0, src0, _ = members[0]
        blocks0, html0 = parse(ARCHIVE / src0)
        title = clean_title(html_title(html0), dest)
        titles[dest] = title
        if out_path.exists():
            front, _ = read_front(out_path)
            if front.get("edited") == "true":
                report["kept_edited"].append(dest)
                if json.loads(front.get("source_sha256", '""')) != sha256(ARCHIVE / src0):
                    report["stale_edited"].append(dest)
                # still resolve its links/images so assets get copied
                Cleaner(resolver, src0, dest).blocks(blocks0)
                for _, src, _ in members[1:]:
                    Cleaner(resolver, src, dest).blocks(parse(ARCHIVE / src)[0])
                continue

        body_blocks = dedupe_headers(Cleaner(resolver, src0, dest).blocks(blocks0))
        md = to_markdown(body_blocks)
        merged = []
        for role, src, note in members[1:]:
            blocks, html = parse(ARCHIVE / src)
            sec = dedupe_headers(Cleaner(resolver, src, dest).blocks(blocks))
            heading = note[:1].upper() + note[1:] if note else clean_title(html_title(html), dest)
            md += f"\n## {heading}\n\n" + to_markdown(sec)
            merged.append({"source": MAP_URL(src), "archive_path": f"archive/www.livingneighborhoods.org/{src}",
                           "source_sha256": sha256(ARCHIVE / src)})

        phase = dest.rsplit("/", 1)[0]
        if phase in phases and dest in phases[phase]:
            steps = phases[phase]
            i = steps.index(dest)
            nav = []
            if i > 0:
                nav.append(f"← [{{{{prev}}}}]({rel(dest, steps[i-1] + '.md')})|{steps[i-1]}")
            if i < len(steps) - 1:
                nav.append(f"→ [{{{{next}}}}]({rel(dest, steps[i+1] + '.md')})|{steps[i+1]}")
            md += "\n<!--NAV " + json.dumps(nav) + " -->\n"

        fields = {
            "title": title,
            "description": description(md),
            "source": MAP_URL(src0),
            "archive_path": f"archive/www.livingneighborhoods.org/{src0}",
            "source_sha256": sha256(ARCHIVE / src0),
            "merged_from": merged,
        }
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(frontmatter(fields) + md, encoding="utf-8")
        report["written"] += 1

    # second pass: fill nav placeholders with titles, add credit line
    for dest in groups:
        path = EDITION / f"{dest}.md"
        text = path.read_text(encoding="utf-8")
        front, _ = read_front(path)
        if front.get("edited") == "true":
            continue
        m = re.search(r"\n<!--NAV (.*) -->\n", text)
        if m:
            parts = []
            for item in json.loads(m.group(1)):
                link, target = item.rsplit("|", 1)
                parts.append(link.replace("{{prev}}", titles[target]).replace("{{next}}", titles[target]))
            phase_title = titles.get(dest.rsplit("/", 1)[0] + "/index", "This phase")
            parts.insert(1 if len(parts) > 1 or parts and parts[0].startswith("←") else 0,
                         f"↑ [{phase_title}](index.md)")
            text = text.replace(m.group(0), "\n---\n\n" + " · ".join(parts) + "\n")
        source = json.loads(front["source"])
        text = text.rstrip() + "\n\n" + CREDIT.format(source=source) + "\n"
        path.write_text(text, encoding="utf-8")

    # PDFs are all kept, linked or not
    for pdf in ARCHIVE.rglob("*.pdf"):
        resolver.assets.add(pdf.relative_to(ARCHIVE).as_posix())
    copied = 0
    for a in sorted(resolver.assets):
        target = EDITION / ASSETS / a
        if not target.exists() or target.stat().st_size != (ARCHIVE / a).stat().st_size:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ARCHIVE / a, target)
            copied += 1
    build_dir = EDITION / "_build"
    build_dir.mkdir(exist_ok=True)
    (build_dir / "links.json").write_text(json.dumps(resolver.dead, indent=1), encoding="utf-8")
    (build_dir / "titles.json").write_text(json.dumps(titles, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {report['written']} pages; kept {len(report['kept_edited'])} hand-edited "
          f"({len(report['stale_edited'])} with changed sources); {len(resolver.assets)} assets "
          f"({copied} copied); {len(resolver.dead)} dead or unmapped links")
    if report["stale_edited"]:
        print("source changed for hand-edited pages:", ", ".join(report["stale_edited"]))


def MAP_URL(src):
    return BASE + ("" if src == "index.html" else src)


if __name__ == "__main__":
    build()
