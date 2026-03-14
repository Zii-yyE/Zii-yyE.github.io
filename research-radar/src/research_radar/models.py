from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PaperIdentifiers:
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    pmid: Optional[str] = None
    pmcid: Optional[str] = None
    biorxiv_doi: Optional[str] = None

    def as_dict(self) -> Dict[str, Optional[str]]:
        return {
            "doi": self.doi,
            "arxiv_id": self.arxiv_id,
            "pmid": self.pmid,
            "pmcid": self.pmcid,
            "biorxiv_doi": self.biorxiv_doi,
        }

    @classmethod
    def from_mapping(cls, value: Optional[Dict[str, Any]]) -> "PaperIdentifiers":
        value = value or {}
        return cls(
            doi=value.get("doi"),
            arxiv_id=value.get("arxiv_id"),
            pmid=value.get("pmid"),
            pmcid=value.get("pmcid"),
            biorxiv_doi=value.get("biorxiv_doi"),
        )


@dataclass
class NormalizedPaper:
    paper_key: str
    title: str
    authors: List[str]
    abstract: str
    published_date: str
    first_seen_at: str
    source_primary: str
    sources: List[str]
    url: str
    venue: str = ""
    identifiers: PaperIdentifiers = field(default_factory=PaperIdentifiers)
    topics: List[str] = field(default_factory=list)
    primary_topic: str = "other"
    matched_keywords: Dict[str, List[str]] = field(default_factory=dict)
    source_record_id: str = ""
    source_url: str = ""

    def to_export_dict(self) -> Dict[str, Any]:
        return {
            "paper_key": self.paper_key,
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "published_date": self.published_date,
            "first_seen_at": self.first_seen_at,
            "source_primary": self.source_primary,
            "sources": self.sources,
            "url": self.url,
            "venue": self.venue,
            "identifiers": self.identifiers.as_dict(),
            "topics": self.topics,
            "primary_topic": self.primary_topic,
            "matched_keywords": self.matched_keywords,
        }

    @classmethod
    def from_mapping(cls, value: Dict[str, Any]) -> "NormalizedPaper":
        return cls(
            paper_key=value["paper_key"],
            title=value["title"],
            authors=list(value.get("authors", [])),
            abstract=value.get("abstract", ""),
            published_date=value.get("published_date", ""),
            first_seen_at=value.get("first_seen_at", ""),
            source_primary=value.get("source_primary", ""),
            sources=list(value.get("sources", [])),
            url=value.get("url", ""),
            venue=value.get("venue", ""),
            identifiers=PaperIdentifiers.from_mapping(value.get("identifiers")),
            topics=list(value.get("topics", [])),
            primary_topic=value.get("primary_topic", "other"),
            matched_keywords=dict(value.get("matched_keywords", {})),
            source_record_id=value.get("source_record_id", ""),
            source_url=value.get("source_url", ""),
        )
