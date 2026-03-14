from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

from .keywords import extract_tracked_keyword_hits
from .models import NormalizedPaper


def _parse_date(value: str) -> Optional[date]:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def _month_bucket(value: str) -> str:
    return value[:7] if len(value) >= 7 else ""


def aggregate_topic_counts_monthly(
    papers: List[NormalizedPaper],
    topics: Dict[str, Dict[str, object]],
) -> Dict[str, object]:
    topic_ids = list(topics.keys())
    counts = defaultdict(lambda: {topic_id: 0 for topic_id in topic_ids})

    for paper in papers:
        month = _month_bucket(paper.published_date)
        if not month:
            continue
        counts[month][paper.primary_topic] += 1

    months = []
    for month in sorted(counts.keys()):
        months.append({"month": month, "counts": counts[month]})
    return {
        "topics": [{"id": topic_id, "label": topics[topic_id].get("label", topic_id)} for topic_id in topic_ids],
        "months": months,
    }


def aggregate_keyword_frequency_monthly(
    papers: List[NormalizedPaper],
    tracked_keywords: List[Dict[str, object]],
) -> Dict[str, object]:
    keyword_ids = [keyword["id"] for keyword in tracked_keywords]
    counts = defaultdict(lambda: {keyword_id: 0 for keyword_id in keyword_ids})

    for paper in papers:
        month = _month_bucket(paper.published_date)
        if not month:
            continue
        for hit in extract_tracked_keyword_hits(paper, tracked_keywords):
            counts[month][hit["id"]] += 1

    months = []
    for month in sorted(counts.keys()):
        months.append({"month": month, "counts": counts[month]})

    return {
        "keywords": [{"id": keyword["id"], "label": keyword.get("label", keyword["id"])} for keyword in tracked_keywords],
        "months": months,
    }


def compute_rising_keywords(
    papers: List[NormalizedPaper],
    tracked_keywords: List[Dict[str, object]],
    recent_days: int,
    baseline_days: int,
    min_recent_count: int,
    reference_date: Optional[date] = None,
) -> Dict[str, object]:
    paper_dates = [_parse_date(paper.published_date) for paper in papers if paper.published_date]
    reference_date = reference_date or (max(paper_dates) if paper_dates else date.today())

    recent_start = reference_date - timedelta(days=max(recent_days - 1, 0))
    baseline_end = recent_start - timedelta(days=1)
    baseline_start = baseline_end - timedelta(days=max(baseline_days - 1, 0))

    recent_total = 0
    baseline_total = 0
    recent_counts = defaultdict(int)
    baseline_counts = defaultdict(int)

    for paper in papers:
        published = _parse_date(paper.published_date)
        if published is None:
            continue
        keyword_hits = extract_tracked_keyword_hits(paper, tracked_keywords)
        if recent_start <= published <= reference_date:
            recent_total += 1
            for hit in keyword_hits:
                recent_counts[hit["id"]] += 1
        elif baseline_start <= published <= baseline_end:
            baseline_total += 1
            for hit in keyword_hits:
                baseline_counts[hit["id"]] += 1

    results = []
    recent_total = max(recent_total, 1)
    baseline_total = max(baseline_total, 1)
    for keyword in tracked_keywords:
        keyword_id = keyword["id"]
        recent_count = recent_counts[keyword_id]
        baseline_count = baseline_counts[keyword_id]
        if recent_count < min_recent_count:
            continue
        recent_rate = recent_count / recent_total
        baseline_rate = baseline_count / baseline_total
        lift = None if baseline_rate == 0 else round(recent_rate / baseline_rate, 4)
        results.append(
            {
                "id": keyword_id,
                "label": keyword.get("label", keyword_id),
                "recent_count": recent_count,
                "baseline_count": baseline_count,
                "recent_rate": round(recent_rate, 4),
                "baseline_rate": round(baseline_rate, 4),
                "delta": round(recent_rate - baseline_rate, 4),
                "lift": lift,
            }
        )

    results.sort(
        key=lambda item: (
            0 if item["lift"] is None else 1,
            -item["delta"],
            -(item["lift"] or 0),
            -item["recent_count"],
            item["label"],
        )
    )
    return {
        "window": {
            "reference_date": reference_date.isoformat(),
            "recent_days": recent_days,
            "baseline_days": baseline_days,
            "min_recent_count": min_recent_count,
        },
        "keywords": results,
    }
