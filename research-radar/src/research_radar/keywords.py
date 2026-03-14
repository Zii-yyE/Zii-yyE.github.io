from __future__ import annotations

from typing import Dict, List

from .classify import find_term_hits
from .models import NormalizedPaper


def extract_tracked_keyword_hits(
    paper: NormalizedPaper,
    tracked_keywords: List[Dict[str, object]],
) -> List[Dict[str, object]]:
    text = f"{paper.title} {paper.abstract}"
    hits: List[Dict[str, object]] = []
    for keyword in tracked_keywords:
        terms = list(keyword.get("terms", []))
        matched_terms = find_term_hits(text, terms)
        if not matched_terms:
            continue
        hits.append(
            {
                "id": keyword["id"],
                "label": keyword.get("label", keyword["id"]),
                "matched_terms": matched_terms,
            }
        )
    return hits
