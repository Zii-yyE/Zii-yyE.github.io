from __future__ import annotations

from typing import Dict, List, Set
from urllib.parse import urlencode

from ..models import NormalizedPaper
from ..normalize import parse_pubmed_article
from .base import chunked, fetch_json, fetch_xml


def _pubmed_query(query: str, start_date: str, end_date: str) -> str:
    date_clause = f'("{start_date}"[Date - Publication] : "{end_date}"[Date - Publication])'
    return f"({query}) AND {date_clause}"


def _esearch_ids(endpoint: str, query: str, retmax: int) -> List[str]:
    identifiers: List[str] = []
    retstart = 0
    while len(identifiers) < retmax:
        batch_size = min(100, retmax - len(identifiers))
        params = urlencode(
            {
                "db": "pubmed",
                "term": query,
                "retmode": "json",
                "retmax": batch_size,
                "retstart": retstart,
                "sort": "pub_date",
            }
        )
        payload = fetch_json(f"{endpoint}?{params}")
        batch = payload.get("esearchresult", {}).get("idlist", [])
        if not batch:
            break
        identifiers.extend(batch)
        retstart += len(batch)
        if len(batch) < batch_size:
            break
    return identifiers


def fetch_pubmed_papers(
    source_config: Dict[str, object],
    start_date: str,
    end_date: str,
    first_seen_at: str,
) -> List[NormalizedPaper]:
    if not source_config.get("enabled", True):
        return []

    esearch_endpoint = str(
        source_config.get("esearch_endpoint", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi")
    )
    efetch_endpoint = str(
        source_config.get("efetch_endpoint", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi")
    )
    retmax = int(source_config.get("retmax", 100))
    unique_ids: List[str] = []
    seen_ids: Set[str] = set()

    for query in source_config.get("queries", []):
        for identifier in _esearch_ids(esearch_endpoint, _pubmed_query(query, start_date, end_date), retmax):
            if identifier in seen_ids:
                continue
            seen_ids.add(identifier)
            unique_ids.append(identifier)

    papers: List[NormalizedPaper] = []
    for batch in chunked(unique_ids, 100):
        params = urlencode({"db": "pubmed", "id": ",".join(batch), "retmode": "xml"})
        root = fetch_xml(f"{efetch_endpoint}?{params}")
        for article in root.findall(".//PubmedArticle"):
            papers.append(parse_pubmed_article(article, first_seen_at))

    return papers
