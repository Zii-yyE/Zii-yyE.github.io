from __future__ import annotations

import time
from typing import Dict, Iterable, List, Optional
from urllib.parse import urlencode

from ..classify import find_term_hits
from ..models import NormalizedPaper
from ..normalize import normalize_biorxiv_item
from .base import fetch_json


def _filter_terms_for_topics(
    source_config: Dict[str, object],
    topic_config: Optional[Dict[str, Dict[str, object]]],
    topic_ids: Optional[Iterable[str]],
) -> Dict[str, List[str]]:
    if not topic_ids:
        return {}

    configured_filters = source_config.get("topic_filters", {})
    if not isinstance(configured_filters, dict):
        configured_filters = {}

    filter_map: Dict[str, List[str]] = {}
    for topic_id in topic_ids:
        filters: List[str] = []
        if topic_config and topic_id in topic_config:
            filters.extend(str(term) for term in topic_config[topic_id].get("include_phrases", []) if term)
            filters.extend(str(term) for term in topic_config[topic_id].get("include_aliases", []) if term)
        topic_terms = configured_filters.get(topic_id, [])
        if isinstance(topic_terms, list):
            filters.extend(str(term) for term in topic_terms if term)
        deduped = []
        for term in filters:
            if term not in deduped:
                deduped.append(term)
        if deduped:
            filter_map[topic_id] = deduped
    return filter_map


def _matches_topic_filters(item: Dict[str, str], filter_map: Dict[str, List[str]]) -> bool:
    if not filter_map:
        return True
    haystack = f"{item.get('title', '')} {item.get('abstract', '')}"
    return any(find_term_hits(haystack, terms) for terms in filter_map.values())


def _biorxiv_url(endpoint: str, start_date: str, end_date: str, cursor: int, category: Optional[str]) -> str:
    base = f"{endpoint}/{start_date}/{end_date}/{cursor}"
    if not category:
        return base
    return f"{base}?{urlencode({'category': category})}"


def fetch_biorxiv_papers(
    source_config: Dict[str, object],
    start_date: str,
    end_date: str,
    first_seen_at: str,
    topic_config: Optional[Dict[str, Dict[str, object]]] = None,
    topic_ids: Optional[Iterable[str]] = None,
    stop_after_matches: Optional[int] = None,
) -> List[NormalizedPaper]:
    if not source_config.get("enabled", True):
        return []

    endpoint = str(source_config.get("endpoint", "https://api.biorxiv.org/details/biorxiv"))
    max_results = int(source_config.get("max_results", 300))
    max_pages_per_category = int(source_config.get("max_pages_per_category", 0) or 0)
    request_interval_seconds = float(source_config.get("request_interval_seconds", 0.0) or 0.0)
    categories: List[Optional[str]] = [str(category) for category in source_config.get("categories", []) if category]
    if not categories:
        categories = [None]

    filter_map = _filter_terms_for_topics(source_config, topic_config, topic_ids)
    papers: List[NormalizedPaper] = []
    target_matches = stop_after_matches or max_results

    for category in categories:
        cursor = 0
        pages_seen = 0
        while len(papers) < target_matches:
            url = _biorxiv_url(endpoint, start_date, end_date, cursor, category)
            payload = fetch_json(url, timeout=45)
            collection = payload.get("collection", [])
            if not collection:
                break

            for item in collection:
                if not _matches_topic_filters(item, filter_map):
                    continue
                papers.append(normalize_biorxiv_item(item, first_seen_at))
                if len(papers) >= target_matches:
                    return papers
                if not filter_map and len(papers) >= max_results:
                    return papers

            messages = payload.get("messages", [{}])
            total = int(messages[0].get("total", 0) or 0)
            cursor += len(collection)
            pages_seen += 1
            if cursor >= total:
                break
            if max_pages_per_category and pages_seen >= max_pages_per_category:
                break
            if request_interval_seconds > 0:
                time.sleep(request_interval_seconds)

    return papers
