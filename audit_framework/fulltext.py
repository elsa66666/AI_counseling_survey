"""Retrieve linked full text once; never send an abstract as a full paper."""
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup
import httpx
from pypdf import PdfReader

from .storage import atomic_write, fingerprint, load_json, save_json


class FulltextError(ValueError):
    pass


def check_identity(title, text):
    words = lambda s: set(re.findall(r"[a-z0-9]+", s.casefold()))
    expected = {w for w in words(title) if len(w) > 2}
    if expected and len(expected & words(text[:8000])) / len(expected) < 0.7:
        raise FulltextError("Downloaded text/title mismatch; inspect the paper URL or supply a verified source")


def pdf_text(data):
    reader = PdfReader(BytesIO(data))
    # Plain extraction includes text nested inside Form XObjects. Layout mode
    # can silently lose nearly the whole paper (e.g. ACL 2024 HealMe).
    pages = [page.extract_text() or "" for page in reader.pages]
    warnings = ["Text extraction does not include figure images; assess missing evidence under INPUT_TRUNCATION."]
    if any(len(page.strip()) < 80 for page in pages):
        warnings.append("Potential input truncation: at least one page has little extractable text (OCR may be required).")
    return "\n\n".join(f"[PDF page {i+1}]\n{p}" for i, p in enumerate(pages)), len(pages), warnings


def extract_html(html):
    soup = BeautifulSoup(html, "html.parser")
    for el in soup.select("script, style, nav, footer, header, .references-links"):
        el.decompose()
    node = soup.select_one("article, .article-body, #articleBody, #main-content")
    if node is None:
        raise FulltextError("Landing page has no identifiable full-text article")
    text = node.get_text("\n", strip=True)
    if len(text) < 6000 or not re.search(r"\b(introduction|background)\b", text, re.I) or not re.search(r"\b(methods?|methodology|implementation|experiment\w*|results)\b", text, re.I):
        raise FulltextError("Page appears to be an abstract/landing page, not usable full text")
    title = soup.select_one('meta[name="citation_title"]')
    return ((title.get("content", "") + "\n") if title else "") + text


def retrieve(paper, cache: Path, source_override=None, client=None):
    directory = cache / paper.paper_id
    text_path, info_path = directory / "paper.txt", directory / "source.json"
    origin = str(source_override or paper.url)
    identity = fingerprint({"metadata": paper.metadata, "source": origin})
    if text_path.exists() and info_path.exists():
        info = load_json(info_path)
        text = text_path.read_text(encoding="utf-8")
        if info.get("input_identity") == identity and info.get("text_sha256") == fingerprint(text):
            paper.content, paper.source = text, info
            return paper
    owned = client is None
    client = client or httpx.Client(follow_redirects=True, timeout=60, headers={"User-Agent": "SFPE-paper-audit/1.0 (academic full-text retrieval)"})
    try:
        directory.mkdir(parents=True, exist_ok=True)
        warnings, pages, source_url, data = [], None, origin, None
        if not origin.startswith(("https://", "http://")):
            local = Path(origin)
            data = local.read_bytes()
            if data.startswith(b"%PDF"):
                text, pages, warnings = pdf_text(data)
            else:
                text = data.decode("utf-8-sig")
        else:
            response = client.get(origin)
            response.raise_for_status()
            source_url = str(response.url)
            if response.content.startswith(b"%PDF"):
                data = response.content
                text, pages, warnings = pdf_text(data)
            else:
                soup = BeautifulSoup(response.text, "html.parser")
                candidates = []
                for meta in soup.select('meta[name="citation_pdf_url"]'):
                    if meta.get("content"):
                        candidates.append(urljoin(source_url, meta["content"]))
                for link in soup.select("a[href]"):
                    href = link["href"]
                    if re.search(r"\.pdf(?:$|\?)", href, re.I) and ("pdf" in link.get_text().lower() or "full" in link.get_text().lower()):
                        candidates.append(urljoin(source_url, href))
                # These repository URLs have a deterministic PDF counterpart.
                parsed = urlsplit(source_url)
                if parsed.hostname == "aclanthology.org":
                    candidates.insert(0, source_url.rstrip("/") + ".pdf")
                elif parsed.hostname == "arxiv.org" and parsed.path.startswith("/abs/"):
                    candidates.insert(0, source_url.replace("/abs/", "/pdf/"))
                text = ""
                for candidate in list(dict.fromkeys(candidates))[:5]:
                    if not candidate.startswith(("https://", "http://")):
                        continue
                    try:
                        pdf = client.get(candidate)
                        pdf.raise_for_status()
                        if not pdf.content.startswith(b"%PDF"):
                            continue
                        candidate_text, candidate_pages, candidate_warnings = pdf_text(pdf.content)
                        check_identity(paper.title, candidate_text)
                        text, pages, warnings = candidate_text, candidate_pages, candidate_warnings
                        data, source_url = pdf.content, str(pdf.url)
                        break
                    except (httpx.HTTPError, FulltextError):
                        continue
                if not text:
                    text = extract_html(response.text)
                    warnings = ["HTML text only; linked figures and supplements are not automatically included."]
                    atomic_write(directory / "paper.html", response.text)
        if len(text.strip()) < 4000:
            raise FulltextError("Insufficient extractable text; no auditor called")
        check_identity(paper.title, text)
        if data and data.startswith(b"%PDF"):
            (directory / "paper.pdf").write_bytes(data)
        info = {"requested_url": paper.url, "source": source_url, "input_identity": identity,
                "text_sha256": fingerprint(text), "characters": len(text), "pages": pages,
                "extraction_warnings": warnings, "retrieved_at": datetime.now(timezone.utc).isoformat()}
        atomic_write(text_path, text)
        save_json(info_path, info)
        paper.content, paper.source = text, info
        return paper
    finally:
        if owned:
            client.close()
