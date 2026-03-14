from __future__ import annotations

from copy import deepcopy
from typing import Dict, List, Optional

from .models import NormalizedPaper, PaperIdentifiers
from .normalize import build_paper_key, normalize_name, normalize_title_key, unique_strings


def _identifier_values(paper: NormalizedPaper) -> Dict[str, str]:
    identifiers = paper.identifiers.as_dict()
    return {key: value for key, value in identifiers.items() if value}


def _first_author_key(paper: NormalizedPaper) -> str:
    if not paper.authors:
        return ""
    return normalize_name(paper.authors[0])


def _publication_year(paper: NormalizedPaper) -> str:
    return paper.published_date[:4] if paper.published_date else ""


def _titles_match(left: NormalizedPaper, right: NormalizedPaper) -> bool:
    return normalize_title_key(left.title) == normalize_title_key(right.title)


def _authors_compatible(left: NormalizedPaper, right: NormalizedPaper) -> bool:
    left_author = _first_author_key(left)
    right_author = _first_author_key(right)
    if left_author and right_author:
        return left_author == right_author
    return True


def _years_compatible(left: NormalizedPaper, right: NormalizedPaper) -> bool:
    left_year = _publication_year(left)
    right_year = _publication_year(right)
    if left_year and right_year:
        return left_year == right_year
    return True


def find_duplicate_index(existing_papers: List[NormalizedPaper], incoming: NormalizedPaper) -> Optional[int]:
    incoming_identifiers = _identifier_values(incoming)
    if incoming_identifiers:
        for index, existing in enumerate(existing_papers):
            existing_identifiers = _identifier_values(existing)
            if any(existing_identifiers.get(key) == value for key, value in incoming_identifiers.items()):
                return index

    for index, existing in enumerate(existing_papers):
        if _titles_match(existing, incoming) and _authors_compatible(existing, incoming) and _years_compatible(existing, incoming):
            return index
    return None


def _merge_identifiers(left: PaperIdentifiers, right: PaperIdentifiers) -> PaperIdentifiers:
    return PaperIdentifiers(
        doi=left.doi or right.doi,
        arxiv_id=left.arxiv_id or right.arxiv_id,
        pmid=left.pmid or right.pmid,
        pmcid=left.pmcid or right.pmcid,
        biorxiv_doi=left.biorxiv_doi or right.biorxiv_doi,
    )


def _merge_matched_keywords(left: Dict[str, List[str]], right: Dict[str, List[str]]) -> Dict[str, List[str]]:
    merged: Dict[str, List[str]] = {}
    for mapping in (left, right):
        for topic, hits in mapping.items():
            merged.setdefault(topic, [])
            for hit in hits:
                if hit not in merged[topic]:
                    merged[topic].append(hit)
    return merged


def merge_papers(existing: NormalizedPaper, incoming: NormalizedPaper) -> NormalizedPaper:
    merged = deepcopy(existing)
    merged.title = existing.title if len(existing.title) >= len(incoming.title) else incoming.title
    merged.authors = existing.authors or incoming.authors
    merged.abstract = existing.abstract if len(existing.abstract) >= len(incoming.abstract) else incoming.abstract
    if existing.published_date and incoming.published_date:
        merged.published_date = min(existing.published_date, incoming.published_date)
    else:
        merged.published_date = existing.published_date or incoming.published_date
    merged.url = existing.url or incoming.url
    merged.venue = existing.venue or incoming.venue
    merged.identifiers = _merge_identifiers(existing.identifiers, incoming.identifiers)
    merged.sources = unique_strings(list(existing.sources) + list(incoming.sources))
    merged.topics = unique_strings(list(existing.topics) + list(incoming.topics))
    merged.primary_topic = existing.primary_topic if existing.primary_topic != "other" else incoming.primary_topic
    merged.matched_keywords = _merge_matched_keywords(existing.matched_keywords, incoming.matched_keywords)
    merged.first_seen_at = existing.first_seen_at or incoming.first_seen_at
    merged.source_record_id = incoming.source_record_id or existing.source_record_id
    merged.source_url = incoming.source_url or existing.source_url or merged.url
    merged.paper_key = build_paper_key(merged)
    return merged


def deduplicate_papers(papers: List[NormalizedPaper]) -> List[NormalizedPaper]:
    canonical: List[NormalizedPaper] = []
    for paper in papers:
        duplicate_index = find_duplicate_index(canonical, paper)
        if duplicate_index is None:
            canonical.append(deepcopy(paper))
            continue
        canonical[duplicate_index] = merge_papers(canonical[duplicate_index], paper)
    return canonical
