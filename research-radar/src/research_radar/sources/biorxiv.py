from __future__ import annotations

from typing import Dict, List

from ..models import NormalizedPaper
from ..normalize import normalize_biorxiv_item
from .base import fetch_json


def fetch_biorxiv_papers(
    source_config: Dict[str, object],
    start_date: str,
    end_date: str,
    first_seen_at: str,
) -> List[NormalizedPaper]:
    if not source_config.get("enabled", True):
        return []

    endpoint = str(source_config.get("endpoint", "https://api.biorxiv.org/details/biorxiv"))
    max_results = int(source_config.get("max_results", 300))
    papers: List[NormalizedPaper] = []
    cursor = 0

    while len(papers) < max_results:
        url = f"{endpoint}/{start_date}/{end_date}/{cursor}"
        payload = fetch_json(url)
        collection = payload.get("collection", [])
        if not collection:
            break

        remaining = max_results - len(papers)
        for item in collection[:remaining]:
            papers.append(normalize_biorxiv_item(item, first_seen_at))

        messages = payload.get("messages", [{}])
        total = int(messages[0].get("total", 0) or 0)
        cursor += len(collection)
        if cursor >= total:
            break

    return papers
