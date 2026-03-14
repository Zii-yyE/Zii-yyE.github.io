from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from typing import Dict, Iterable, List, Optional
from xml.etree import ElementTree as ET

from .models import NormalizedPaper, PaperIdentifiers


ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def normalize_whitespace(value: Optional[str]) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def normalize_search_text(value: Optional[str]) -> str:
    text = normalize_whitespace(value).lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return normalize_whitespace(text)


def normalize_title_key(value: Optional[str]) -> str:
    return normalize_search_text(value)


def normalize_name(value: Optional[str]) -> str:
    return normalize_search_text(value)


def normalize_doi(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    cleaned = normalize_whitespace(value).lower()
    cleaned = re.sub(r"^https?://(dx\.)?doi\.org/", "", cleaned)
    cleaned = re.sub(r"^doi:\s*", "", cleaned)
    cleaned = cleaned.strip().strip(".")
    return cleaned or None


def parse_date_string(value: Optional[str]) -> str:
    cleaned = normalize_whitespace(value)
    if not cleaned:
        return ""
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", cleaned):
        return cleaned
    if re.fullmatch(r"\d{4}/\d{2}/\d{2}", cleaned):
        return cleaned.replace("/", "-")
    if re.fullmatch(r"\d{4}-\d{2}", cleaned):
        return f"{cleaned}-01"
    if re.fullmatch(r"\d{4}", cleaned):
        return f"{cleaned}-01-01"
    cleaned = cleaned.replace("/", "-")
    for fmt in (
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y %m %d",
        "%Y %b %d",
        "%Y %B %d",
        "%b %d %Y",
        "%B %d %Y",
    ):
        try:
            return datetime.strptime(cleaned, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return cleaned[:10] if len(cleaned) >= 10 else cleaned


def month_to_number(value: str) -> str:
    try:
        return datetime.strptime(value[:3], "%b").strftime("%m")
    except ValueError:
        return "01"


def slugify(value: str, max_length: int = 80) -> str:
    normalized = normalize_title_key(value)
    if not normalized:
        return "paper"
    slug = normalized.replace(" ", "-")
    slug = slug[:max_length].strip("-")
    return slug or "paper"


def build_paper_key(paper: NormalizedPaper) -> str:
    identifiers = paper.identifiers
    if identifiers.doi:
        return f"doi:{identifiers.doi}"
    if identifiers.arxiv_id:
        return f"arxiv:{identifiers.arxiv_id}"
    if identifiers.pmid:
        return f"pmid:{identifiers.pmid}"
    if identifiers.biorxiv_doi:
        return f"biorxiv:{identifiers.biorxiv_doi}"
    return f"title:{slugify(paper.title)}:{paper.published_date or 'unknown'}"


def split_biorxiv_authors(value: Optional[str]) -> List[str]:
    cleaned = normalize_whitespace(value)
    if not cleaned:
        return []
    if ";" in cleaned:
        pieces = cleaned.split(";")
    else:
        pieces = cleaned.split(",")
    return [normalize_whitespace(piece) for piece in pieces if normalize_whitespace(piece)]


def normalize_biorxiv_item(item: Dict[str, str], first_seen_at: str) -> NormalizedPaper:
    preprint_doi = normalize_doi(item.get("doi"))
    published_doi = normalize_doi(item.get("published"))
    url = f"https://doi.org/{preprint_doi}" if preprint_doi else item.get("jatsxml", "")
    paper = NormalizedPaper(
        paper_key="",
        title=normalize_whitespace(item.get("title")),
        authors=split_biorxiv_authors(item.get("authors")),
        abstract=normalize_whitespace(item.get("abstract")),
        published_date=parse_date_string(item.get("date")),
        first_seen_at=first_seen_at,
        source_primary="biorxiv",
        sources=["biorxiv"],
        url=url,
        venue="bioRxiv",
        identifiers=PaperIdentifiers(
            doi=published_doi or preprint_doi,
            biorxiv_doi=preprint_doi,
        ),
        source_record_id=preprint_doi or slugify(item.get("title", "")),
        source_url=url,
    )
    paper.paper_key = build_paper_key(paper)
    return paper


def parse_arxiv_entry(entry: ET.Element, first_seen_at: str) -> NormalizedPaper:
    title = normalize_whitespace(entry.findtext("atom:title", default="", namespaces=ARXIV_NS))
    abstract = normalize_whitespace(entry.findtext("atom:summary", default="", namespaces=ARXIV_NS))
    published = parse_date_string(entry.findtext("atom:published", default="", namespaces=ARXIV_NS))
    raw_id = normalize_whitespace(entry.findtext("atom:id", default="", namespaces=ARXIV_NS))
    arxiv_id = raw_id.rsplit("/", 1)[-1].split("v", 1)[0] if raw_id else None
    authors = [
        normalize_whitespace(author.findtext("atom:name", default="", namespaces=ARXIV_NS))
        for author in entry.findall("atom:author", ARXIV_NS)
    ]
    doi = normalize_doi(entry.findtext("arxiv:doi", default="", namespaces=ARXIV_NS))
    paper = NormalizedPaper(
        paper_key="",
        title=title,
        authors=[author for author in authors if author],
        abstract=abstract,
        published_date=published,
        first_seen_at=first_seen_at,
        source_primary="arxiv",
        sources=["arxiv"],
        url=raw_id,
        venue="arXiv",
        identifiers=PaperIdentifiers(doi=doi, arxiv_id=arxiv_id),
        source_record_id=arxiv_id or slugify(title),
        source_url=raw_id,
    )
    paper.paper_key = build_paper_key(paper)
    return paper


def _text_content(node: Optional[ET.Element]) -> str:
    if node is None:
        return ""
    return normalize_whitespace("".join(node.itertext()))


def _pubmed_authors(article: ET.Element) -> List[str]:
    authors: List[str] = []
    for author in article.findall(".//AuthorList/Author"):
        collective = _text_content(author.find("CollectiveName"))
        if collective:
            authors.append(collective)
            continue
        fore_name = _text_content(author.find("ForeName"))
        last_name = _text_content(author.find("LastName"))
        full_name = normalize_whitespace(" ".join(piece for piece in (fore_name, last_name) if piece))
        if full_name:
            authors.append(full_name)
    return authors


def _date_from_parts(year: str, month: str, day: str) -> str:
    if year and month and day:
        month_value = month.zfill(2) if month.isdigit() else month_to_number(month)
        return f"{year}-{month_value}-{day.zfill(2)}"
    if year and month:
        month_value = month.zfill(2) if month.isdigit() else month_to_number(month)
        return f"{year}-{month_value}-01"
    if year:
        return f"{year}-01-01"
    return ""


def _date_from_node(node: Optional[ET.Element]) -> str:
    if node is None:
        return ""
    return _date_from_parts(
        _text_content(node.find("Year")),
        _text_content(node.find("Month")),
        _text_content(node.find("Day")),
    )


def _pubmed_published_date(article: ET.Element) -> str:
    for node in article.findall(".//ArticleDate"):
        parsed = _date_from_node(node)
        if parsed:
            return parsed

    for status in ("pubmed", "entrez", "epublish", "aheadofprint", "accepted"):
        for node in article.findall(f".//PubMedPubDate[@PubStatus='{status}']"):
            parsed = _date_from_node(node)
            if parsed:
                return parsed

    for path in (
        ".//PubDate",
        ".//DateCompleted",
        ".//DateRevised",
    ):
        parsed = _date_from_node(article.find(path))
        if parsed:
            return parsed
    return ""


def _pubmed_venue(article: ET.Element) -> str:
    for path in (
        ".//Journal/ISOAbbreviation",
        ".//MedlineJournalInfo/MedlineTA",
        ".//Journal/Title",
    ):
        value = _text_content(article.find(path))
        if value:
            return value
    return "PubMed"


def parse_pubmed_article(article: ET.Element, first_seen_at: str) -> NormalizedPaper:
    title = _text_content(article.find(".//ArticleTitle"))
    abstract_parts = [
        _text_content(node)
        for node in article.findall(".//Abstract/AbstractText")
        if _text_content(node)
    ]
    abstract = normalize_whitespace(" ".join(abstract_parts))
    pmid = _text_content(article.find(".//PMID"))
    doi = None
    pmcid = None
    for article_id in article.findall(".//ArticleIdList/ArticleId"):
        id_type = normalize_whitespace(article_id.attrib.get("IdType", "")).lower()
        value = _text_content(article_id)
        if id_type == "doi":
            doi = normalize_doi(value)
        elif id_type == "pmc":
            pmcid = value
    url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""
    paper = NormalizedPaper(
        paper_key="",
        title=title,
        authors=_pubmed_authors(article),
        abstract=abstract,
        published_date=_pubmed_published_date(article),
        first_seen_at=first_seen_at,
        source_primary="pubmed",
        sources=["pubmed"],
        url=url,
        venue=_pubmed_venue(article),
        identifiers=PaperIdentifiers(doi=doi, pmid=pmid, pmcid=pmcid),
        source_record_id=pmid or slugify(title),
        source_url=url,
    )
    paper.paper_key = build_paper_key(paper)
    return paper


def unique_strings(values: Iterable[str]) -> List[str]:
    seen = set()
    result = []
    for value in values:
        cleaned = normalize_whitespace(value)
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            result.append(cleaned)
    return result
