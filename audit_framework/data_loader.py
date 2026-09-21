from dataclasses import dataclass, field
import json
from pathlib import Path
import re


@dataclass
class Paper:
    paper_id: str
    title: str
    url: str
    metadata: dict
    content: str = ""
    source: dict = field(default_factory=dict)


def bib_field(bib, name):
    match = re.search(r"\b" + name + r'\s*=\s*([{"])', bib, re.I)
    if not match:
        return ""
    if match[1] == '"':
        end = re.search(r'(?<!\\)"', bib[match.end():])
        if not end:
            raise ValueError(f"Unclosed quoted BibTeX field: {name}")
        return " ".join(bib[match.end():match.end()+end.start()].replace("{", "").replace("}", "").split())
    start, depth = match.end(), 1
    for i in range(start, len(bib)):
        if bib[i] == "{" and (i == 0 or bib[i-1] != "\\"):
            depth += 1
        elif bib[i] == "}" and (i == 0 or bib[i-1] != "\\"):
            depth -= 1
        if depth == 0:
            return bib[start:i].replace("{", "").replace("}", "")
    raise ValueError(f"Unbalanced BibTeX field: {name}")


def load_papers(path: Path):
    records = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(records, list):
        raise ValueError("Expected a JSON array of bib/url records")
    papers, seen = [], set()
    for record in records:
        if not isinstance(record, dict) or not all(isinstance(record.get(k), str) for k in ("bib", "url")):
            raise ValueError("Each paper requires string bib and url fields")
        match = re.search(r"@\w+\s*\{\s*([^,]+)", record["bib"])
        if not match:
            raise ValueError("Missing BibTeX citation key")
        paper_id = match[1].strip()
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", paper_id) or paper_id.endswith("."):
            raise ValueError(f"Unsafe paper ID: {paper_id}")
        if paper_id.casefold() in seen:
            raise ValueError(f"Duplicate paper ID: {paper_id}")
        seen.add(paper_id.casefold())
        title = bib_field(record["bib"], "title")
        if not title:
            raise ValueError(f"Missing title: {paper_id}")
        metadata = {**record, "paper_id": paper_id, "title": title,
                    "year": bib_field(record["bib"], "year"), "authors": bib_field(record["bib"], "author")}
        papers.append(Paper(paper_id, title, record["url"], metadata))
    return papers


def load_prompt(path):
    text = Path(path).read_text(encoding="utf-8-sig")
    if not text.strip() or text.count("{{FULL_PAPER}}") != 1:
        raise ValueError("Protocol must contain exactly one {{FULL_PAPER}} placeholder")
    return text
