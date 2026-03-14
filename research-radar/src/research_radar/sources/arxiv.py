from __future__ import annotations

import time
from typing import Dict, List, Set
from urllib.parse import urlencode

from ..models import NormalizedPaper
from ..normalize import ARXIV_NS, parse_arxiv_entry
from .base import fetch_xml


def _arxiv_range_clause(start_date: str, end_date: str) -> str:
    start = start_date.replace("-", "") + "0000"
    end = end_date.replace("-", "") + "2359"
    return f"submittedDate:[{start} TO {end}]"


def fetch_arxiv_papers(
    source_config: Dict[str, object],
    start_date: str,
    end_date: str,
    first_seen_at: str,
) -> List[NormalizedPaper]:
    if not source_config.get("enabled", True):
        return []

    endpoint = str(source_config.get("endpoint", "https://export.arxiv.org/api/query"))
    max_per_query = int(source_config.get("max_results_per_query", 50))
    request_interval_seconds = float(source_config.get("request_interval_seconds", 3.5))
    queries = [query for query in source_config.get("queries", []) if query]
    if not queries:
        return []

    max_results = max_per_query * len(queries)
    papers: List[NormalizedPaper] = []
    seen_ids: Set[str] = set()

    search_query = f"({' OR '.join(f'({query})' for query in queries)}) AND {_arxiv_range_clause(start_date, end_date)}"
    fetched = 0
    offset = 0
    while fetched < max_results:
        batch_size = min(100, max_results - fetched)
        params = urlencode(
            {
                "search_query": search_query,
                "start": offset,
                "max_results": batch_size,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
            }
        )
        root = fetch_xml(f"{endpoint}?{params}")
        entries = root.findall("atom:entry", ARXIV_NS)
        if not entries:
            break

        for entry in entries:
            paper = parse_arxiv_entry(entry, first_seen_at)
            if not paper.source_record_id or paper.source_record_id in seen_ids:
                continue
            seen_ids.add(paper.source_record_id)
            papers.append(paper)

        fetched += len(entries)
        offset += len(entries)
        if len(entries) < batch_size:
            break
        time.sleep(request_interval_seconds)

    return papers
