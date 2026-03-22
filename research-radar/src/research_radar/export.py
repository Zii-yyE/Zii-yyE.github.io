from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .classify import classify_papers
from .models import NormalizedPaper

TOPIC_ACCENT_COLORS = {
    "mutation_rate": "#f25f4c",
    "arg": "#2d6cdf",
    "recombination": "#8b5e34",
    "pangenome_sv": "#2f8f6b",
    "other": "#6b7280",
}

SOURCE_LABELS = {
    "biorxiv": "bioRxiv",
    "pubmed": "PubMed",
    "arxiv": "arXiv",
}

STALE_OUTPUT_FILES = (
    "topic_counts_monthly.json",
    "keyword_frequency_monthly.json",
    "rising_keywords.json",
)


def _write_json(path: Path, payload: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _remove_stale_outputs(output_path: Path) -> None:
    for filename in STALE_OUTPUT_FILES:
        path = output_path / filename
        if path.exists():
            path.unlink()


def _china_time_display(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        return ""
    try:
        parsed = datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
    except ValueError:
        return cleaned
    china_time = parsed.astimezone(timezone(timedelta(hours=8)))
    return china_time.strftime("%Y-%m-%d %H:%M UTC+8")


def _build_summary(
    papers: List[NormalizedPaper],
    config: Dict[str, object],
    generated_at: str,
    metadata: Dict[str, object],
) -> Dict[str, object]:
    topic_counts: Dict[str, int] = {}
    focus_topic_ids = list(config.get("paper_watch", {}).get("topic_ids", []))

    for paper in papers:
        topic_counts[paper.primary_topic] = topic_counts.get(paper.primary_topic, 0) + 1

    focus_topics = []
    for topic_id in focus_topic_ids:
        topic_config = config["topics"].get(topic_id, {})
        focus_topics.append(
            {
                "id": topic_id,
                "label": topic_config.get("label", topic_id),
                "accent_color": TOPIC_ACCENT_COLORS.get(topic_id, TOPIC_ACCENT_COLORS["other"]),
                "count": topic_counts.get(topic_id, 0),
            }
        )

    return {
        "generated_at": generated_at,
        "generated_at_china": _china_time_display(generated_at),
        "focus_topics": focus_topics,
        "source_errors": metadata.get("source_errors", {}),
    }


def _truncate_text(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value
    clipped = value[: max_length - 1].rsplit(" ", 1)[0].rstrip()
    return f"{clipped}..."


def _authors_display(authors: List[str]) -> str:
    if len(authors) <= 3:
        return ", ".join(authors)
    return ", ".join(authors[:3]) + ", et al."


def _venue_display(paper: NormalizedPaper) -> str:
    venue = paper.venue.strip()
    if venue:
        return _truncate_text(venue, 52)
    return SOURCE_LABELS.get(paper.source_primary, paper.source_primary)


def _paper_display_dict(paper: NormalizedPaper, config: Dict[str, object]) -> Dict[str, object]:
    topic_config = config["topics"].get(paper.primary_topic, {})
    payload = paper.to_export_dict()
    payload.update(
        {
            "authors_display": _authors_display(paper.authors),
            "short_abstract": _truncate_text(paper.abstract, 340),
            "primary_topic_label": topic_config.get("label", paper.primary_topic),
            "accent_color": TOPIC_ACCENT_COLORS.get(paper.primary_topic, TOPIC_ACCENT_COLORS["other"]),
            "venue_display": _venue_display(paper),
        }
    )
    return payload


def _focus_topic_ids(config: Dict[str, object]) -> List[str]:
    topic_ids = list(config.get("paper_watch", {}).get("topic_ids", []))
    return [topic_id for topic_id in topic_ids if topic_id in config.get("topics", {})]


def _focus_papers(papers: List[NormalizedPaper], config: Dict[str, object]) -> List[NormalizedPaper]:
    focus_topic_ids = set(_focus_topic_ids(config))
    return [paper for paper in papers if paper.primary_topic in focus_topic_ids]


def _sort_papers(papers: List[NormalizedPaper]) -> List[NormalizedPaper]:
    return sorted(
        papers,
        key=lambda paper: (paper.published_date, paper.first_seen_at, paper.paper_key),
        reverse=True,
    )


def _selected_recent_papers(papers: List[NormalizedPaper], config: Dict[str, object]) -> List[NormalizedPaper]:
    focus_topic_ids = _focus_topic_ids(config)
    minimum_per_topic = int(config.get("paper_watch", {}).get("minimum_per_topic", 0) or 0)
    requested_limit = int(config["exports"]["recent_limit"])
    effective_limit = max(requested_limit, minimum_per_topic * len(focus_topic_ids))
    sorted_papers = _sort_papers(_focus_papers(papers, config))

    selected: List[NormalizedPaper] = []
    selected_keys = set()

    if minimum_per_topic > 0:
        for topic_id in focus_topic_ids:
            topic_papers = [paper for paper in sorted_papers if paper.primary_topic == topic_id]
            for paper in topic_papers[:minimum_per_topic]:
                if paper.paper_key in selected_keys:
                    continue
                selected.append(paper)
                selected_keys.add(paper.paper_key)

    for paper in sorted_papers:
        if len(selected) >= effective_limit:
            break
        if paper.paper_key in selected_keys:
            continue
        selected.append(paper)
        selected_keys.add(paper.paper_key)

    return _sort_papers(selected)


def export_outputs(
    papers: List[NormalizedPaper],
    config: Dict[str, object],
    output_dir: str,
    generated_at: str,
    metadata: Optional[Dict[str, object]] = None,
) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    metadata = metadata or {}

    classify_papers(papers, config["topics"])
    focus_sorted_papers = _sort_papers(_focus_papers(papers, config))
    recent_papers = _selected_recent_papers(papers, config)

    recent_payload = {
        "generated_at": generated_at,
        "latest": [_paper_display_dict(paper, config) for paper in recent_papers],
    }
    summary_payload = _build_summary(focus_sorted_papers, config, generated_at, metadata)

    _write_json(output_path / "recent_papers.json", recent_payload)
    _write_json(output_path / "summary.json", summary_payload)
    _remove_stale_outputs(output_path)
