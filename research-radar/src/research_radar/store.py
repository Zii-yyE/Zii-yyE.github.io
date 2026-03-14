from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple

from .dedupe import find_duplicate_index, merge_papers
from .models import NormalizedPaper
from .normalize import build_paper_key, normalize_name, normalize_title_key


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_key TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    title_normalized TEXT NOT NULL,
    authors_json TEXT NOT NULL,
    first_author_normalized TEXT,
    abstract TEXT NOT NULL,
    published_date TEXT,
    published_year TEXT,
    source_primary TEXT NOT NULL,
    sources_json TEXT NOT NULL,
    url TEXT NOT NULL,
    venue TEXT NOT NULL DEFAULT '',
    doi TEXT,
    arxiv_id TEXT,
    pmid TEXT,
    pmcid TEXT,
    biorxiv_doi TEXT,
    topics_json TEXT NOT NULL,
    primary_topic TEXT NOT NULL,
    matched_keywords_json TEXT NOT NULL,
    first_seen_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_papers_doi ON papers(doi);
CREATE INDEX IF NOT EXISTS idx_papers_arxiv_id ON papers(arxiv_id);
CREATE INDEX IF NOT EXISTS idx_papers_pmid ON papers(pmid);
CREATE INDEX IF NOT EXISTS idx_papers_title_normalized ON papers(title_normalized);

CREATE TABLE IF NOT EXISTS paper_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER NOT NULL,
    source_name TEXT NOT NULL,
    source_record_id TEXT NOT NULL,
    source_url TEXT NOT NULL,
    first_seen_at TEXT NOT NULL,
    UNIQUE(source_name, source_record_id),
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE
);
"""


def _ensure_schema(connection: sqlite3.Connection) -> None:
    columns = {row["name"] for row in connection.execute("PRAGMA table_info(papers)").fetchall()}
    if "venue" not in columns:
        connection.execute("ALTER TABLE papers ADD COLUMN venue TEXT NOT NULL DEFAULT ''")
        connection.commit()


def connect_database(path: str) -> sqlite3.Connection:
    database_path = Path(path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(database_path))
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    _ensure_schema(connection)
    return connection


def _paper_from_row(row: sqlite3.Row) -> NormalizedPaper:
    return NormalizedPaper.from_mapping(
        {
            "paper_key": row["paper_key"],
            "title": row["title"],
            "authors": json.loads(row["authors_json"]),
            "abstract": row["abstract"],
            "published_date": row["published_date"],
            "first_seen_at": row["first_seen_at"],
            "source_primary": row["source_primary"],
            "sources": json.loads(row["sources_json"]),
            "url": row["url"],
            "venue": row["venue"],
            "identifiers": {
                "doi": row["doi"],
                "arxiv_id": row["arxiv_id"],
                "pmid": row["pmid"],
                "pmcid": row["pmcid"],
                "biorxiv_doi": row["biorxiv_doi"],
            },
            "topics": json.loads(row["topics_json"]),
            "primary_topic": row["primary_topic"],
            "matched_keywords": json.loads(row["matched_keywords_json"]),
        }
    )


def load_all_papers(connection: sqlite3.Connection) -> List[NormalizedPaper]:
    rows = connection.execute("SELECT * FROM papers ORDER BY published_date DESC, id DESC").fetchall()
    return [_paper_from_row(row) for row in rows]


def _load_existing(connection: sqlite3.Connection) -> List[Tuple[int, NormalizedPaper]]:
    rows = connection.execute("SELECT * FROM papers ORDER BY id ASC").fetchall()
    return [(row["id"], _paper_from_row(row)) for row in rows]


def _paper_values(paper: NormalizedPaper, updated_at: str) -> Dict[str, object]:
    paper.paper_key = build_paper_key(paper)
    return {
        "paper_key": paper.paper_key,
        "title": paper.title,
        "title_normalized": normalize_title_key(paper.title),
        "authors_json": json.dumps(paper.authors, ensure_ascii=False),
        "first_author_normalized": normalize_name(paper.authors[0]) if paper.authors else "",
        "abstract": paper.abstract,
        "published_date": paper.published_date,
        "published_year": paper.published_date[:4] if paper.published_date else "",
        "source_primary": paper.source_primary,
        "sources_json": json.dumps(paper.sources, ensure_ascii=False),
        "url": paper.url,
        "venue": paper.venue,
        "doi": paper.identifiers.doi,
        "arxiv_id": paper.identifiers.arxiv_id,
        "pmid": paper.identifiers.pmid,
        "pmcid": paper.identifiers.pmcid,
        "biorxiv_doi": paper.identifiers.biorxiv_doi,
        "topics_json": json.dumps(paper.topics, ensure_ascii=False),
        "primary_topic": paper.primary_topic,
        "matched_keywords_json": json.dumps(paper.matched_keywords, ensure_ascii=False),
        "first_seen_at": paper.first_seen_at,
        "updated_at": updated_at,
    }


def _insert_paper(connection: sqlite3.Connection, paper: NormalizedPaper, updated_at: str) -> int:
    values = _paper_values(paper, updated_at)
    cursor = connection.execute(
        """
        INSERT INTO papers (
            paper_key, title, title_normalized, authors_json, first_author_normalized,
            abstract, published_date, published_year, source_primary, sources_json,
            url, venue, doi, arxiv_id, pmid, pmcid, biorxiv_doi,
            topics_json, primary_topic, matched_keywords_json, first_seen_at, updated_at
        ) VALUES (
            :paper_key, :title, :title_normalized, :authors_json, :first_author_normalized,
            :abstract, :published_date, :published_year, :source_primary, :sources_json,
            :url, :venue, :doi, :arxiv_id, :pmid, :pmcid, :biorxiv_doi,
            :topics_json, :primary_topic, :matched_keywords_json, :first_seen_at, :updated_at
        )
        """,
        values,
    )
    return int(cursor.lastrowid)


def _update_paper(connection: sqlite3.Connection, paper_id: int, paper: NormalizedPaper, updated_at: str) -> None:
    values = _paper_values(paper, updated_at)
    values["paper_id"] = paper_id
    connection.execute(
        """
        UPDATE papers SET
            paper_key = :paper_key,
            title = :title,
            title_normalized = :title_normalized,
            authors_json = :authors_json,
            first_author_normalized = :first_author_normalized,
            abstract = :abstract,
            published_date = :published_date,
            published_year = :published_year,
            source_primary = :source_primary,
            sources_json = :sources_json,
            url = :url,
            venue = :venue,
            doi = :doi,
            arxiv_id = :arxiv_id,
            pmid = :pmid,
            pmcid = :pmcid,
            biorxiv_doi = :biorxiv_doi,
            topics_json = :topics_json,
            primary_topic = :primary_topic,
            matched_keywords_json = :matched_keywords_json,
            first_seen_at = :first_seen_at,
            updated_at = :updated_at
        WHERE id = :paper_id
        """,
        values,
    )


def _upsert_source(connection: sqlite3.Connection, paper_id: int, paper: NormalizedPaper) -> None:
    source_record_id = paper.source_record_id or paper.paper_key
    source_url = paper.source_url or paper.url
    connection.execute(
        """
        INSERT OR IGNORE INTO paper_sources (
            paper_id, source_name, source_record_id, source_url, first_seen_at
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (paper_id, paper.source_primary, source_record_id, source_url, paper.first_seen_at),
    )


def upsert_papers(connection: sqlite3.Connection, papers: List[NormalizedPaper], updated_at: str) -> Dict[str, int]:
    existing = _load_existing(connection)
    canonical_papers = [paper for _, paper in existing]
    stats = {"inserted": 0, "updated": 0}

    for incoming in papers:
        duplicate_index = find_duplicate_index(canonical_papers, incoming)
        if duplicate_index is None:
            paper_id = _insert_paper(connection, incoming, updated_at)
            _upsert_source(connection, paper_id, incoming)
            existing.append((paper_id, incoming))
            canonical_papers.append(incoming)
            stats["inserted"] += 1
            continue

        paper_id, current = existing[duplicate_index]
        merged = merge_papers(current, incoming)
        _update_paper(connection, paper_id, merged, updated_at)
        _upsert_source(connection, paper_id, incoming)
        existing[duplicate_index] = (paper_id, merged)
        canonical_papers[duplicate_index] = merged
        stats["updated"] += 1

    connection.commit()
    return stats
