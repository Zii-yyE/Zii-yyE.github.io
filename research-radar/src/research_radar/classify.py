from __future__ import annotations

import re
from typing import Dict, Iterable, List, Tuple

from .models import NormalizedPaper
from .normalize import normalize_search_text


def _ordered_terms(terms: Iterable[str]) -> List[str]:
    normalized = {normalize_search_text(term) for term in terms if normalize_search_text(term)}
    return sorted(normalized, key=lambda term: (-len(term), term))


def _term_pattern(term: str) -> re.Pattern[str]:
    escaped = re.escape(term).replace(r"\ ", r"\s+")
    return re.compile(r"(?<![a-z0-9])" + escaped + r"(?![a-z0-9])")


def find_term_hits(text: str, terms: Iterable[str]) -> List[str]:
    normalized_text = normalize_search_text(text)
    if not normalized_text:
        return []
    hits: List[str] = []
    occupied_spans: List[Tuple[int, int]] = []
    for term in _ordered_terms(terms):
        match = _term_pattern(term).search(normalized_text)
        if match is None or term in hits:
            continue
        start, end = match.span()
        if any(not (end <= occupied_start or start >= occupied_end) for occupied_start, occupied_end in occupied_spans):
            continue
        occupied_spans.append((start, end))
        hits.append(term)
    return hits


def classify_paper(paper: NormalizedPaper, topic_config: Dict[str, Dict[str, object]]) -> NormalizedPaper:
    title_text = normalize_search_text(paper.title)
    abstract_text = normalize_search_text(paper.abstract)
    full_text = normalize_search_text(f"{paper.title} {paper.abstract}")

    scored_topics: List[Tuple[str, int, int]] = []
    matched_keywords: Dict[str, List[str]] = {}

    for topic_id, config in topic_config.items():
        if topic_id == "other":
            continue
        exclude_terms = config.get("exclude_phrases", [])
        if find_term_hits(full_text, exclude_terms):
            continue

        include_terms = list(config.get("include_phrases", [])) + list(config.get("include_aliases", []))
        title_hits = find_term_hits(title_text, include_terms)
        abstract_hits = [hit for hit in find_term_hits(abstract_text, include_terms) if hit not in title_hits]
        score = (3 * len(title_hits)) + len(abstract_hits)
        if score <= 0:
            continue

        required_context_terms = list(config.get("require_any_phrases", []))
        if required_context_terms and not find_term_hits(full_text, required_context_terms):
            continue

        matched_keywords[topic_id] = title_hits + abstract_hits
        priority = int(config.get("priority", 999))
        scored_topics.append((topic_id, score, priority))

    if not scored_topics:
        paper.topics = ["other"]
        paper.primary_topic = "other"
        paper.matched_keywords = {}
        return paper

    scored_topics.sort(key=lambda item: (-item[1], item[2], item[0]))
    paper.topics = [topic_id for topic_id, _, _ in scored_topics]
    paper.primary_topic = scored_topics[0][0]
    paper.matched_keywords = {topic_id: matched_keywords[topic_id] for topic_id in paper.topics}
    return paper


def classify_papers(papers: List[NormalizedPaper], topic_config: Dict[str, Dict[str, object]]) -> List[NormalizedPaper]:
    return [classify_paper(paper, topic_config) for paper in papers]
