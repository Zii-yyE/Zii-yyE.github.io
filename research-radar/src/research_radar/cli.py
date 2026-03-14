from __future__ import annotations

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from .classify import classify_papers, find_term_hits
from .config import load_config
from .export import export_outputs
from .models import NormalizedPaper
from .sources.arxiv import fetch_arxiv_papers
from .sources.biorxiv import fetch_biorxiv_papers
from .sources.pubmed import fetch_pubmed_papers
from .store import connect_database, load_all_papers, upsert_papers


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PACKAGE_ROOT.parent

DEFAULT_CONFIG_PATH = str(PACKAGE_ROOT / "topics.yaml")
DEFAULT_STATE_PATH = str(PACKAGE_ROOT / "state" / "papers.sqlite3")
DEFAULT_DATA_DIR = str(REPO_ROOT / "data" / "research_radar")


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_cli_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def chunk_date_ranges(start_date: date, end_date: date, chunk_days: int) -> Iterable[Tuple[date, date]]:
    current = start_date
    while current <= end_date:
        chunk_end = min(current + timedelta(days=chunk_days - 1), end_date)
        yield current, chunk_end
        current = chunk_end + timedelta(days=1)


def _fetch_all_sources(
    source_config: Dict[str, object],
    start_date: str,
    end_date: str,
    first_seen_at: str,
) -> Tuple[Dict[str, List[NormalizedPaper]], Dict[str, str]]:
    results: Dict[str, List[NormalizedPaper]] = {}
    errors: Dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {}
        if source_config.get("biorxiv", {}).get("enabled", True):
            futures[executor.submit(fetch_biorxiv_papers, source_config["biorxiv"], start_date, end_date, first_seen_at)] = "biorxiv"
        if source_config.get("arxiv", {}).get("enabled", True):
            futures[executor.submit(fetch_arxiv_papers, source_config["arxiv"], start_date, end_date, first_seen_at)] = "arxiv"
        if source_config.get("pubmed", {}).get("enabled", True):
            futures[executor.submit(fetch_pubmed_papers, source_config["pubmed"], start_date, end_date, first_seen_at)] = "pubmed"

        for future in as_completed(futures):
            source_name = futures[future]
            try:
                results[source_name] = future.result()
            except Exception as error:
                errors[source_name] = f"{type(error).__name__}: {error}"
                print(f"[research-radar] source fetch failed: {source_name}: {errors[source_name]}", file=sys.stderr)

    if not results and errors:
        raise RuntimeError("All source fetches failed: " + "; ".join(f"{name}: {message}" for name, message in sorted(errors.items())))
    return results, errors


def _keep_biorxiv_paper(paper: NormalizedPaper, source_config: Dict[str, object]) -> bool:
    if paper.primary_topic != "other":
        return True
    filters = list(source_config.get("local_filters", []))
    if not filters:
        return False
    return bool(find_term_hits(f"{paper.title} {paper.abstract}", filters))


def _collect_and_store_range(
    connection,
    config: Dict[str, object],
    start_date: date,
    end_date: date,
    generated_at: str,
) -> Tuple[Dict[str, int], Dict[str, str]]:
    fetched_by_source, source_errors = _fetch_all_sources(
        config["sources"],
        start_date.isoformat(),
        end_date.isoformat(),
        generated_at,
    )
    classified: List[NormalizedPaper] = []
    for papers in fetched_by_source.values():
        classified.extend(papers)
    classify_papers(classified, config["topics"])

    filtered: List[NormalizedPaper] = []
    for paper in classified:
        if paper.source_primary == "biorxiv" and not _keep_biorxiv_paper(paper, config["sources"]["biorxiv"]):
            continue
        filtered.append(paper)

    return upsert_papers(connection, filtered, updated_at=generated_at), source_errors


def run_update(config_path: str, state_path: str, data_dir: str, days: Optional[int] = None) -> None:
    config = load_config(config_path)
    window_days = days or int(config["defaults"]["update_window_days"])
    end_date = date.today()
    start_date = end_date - timedelta(days=max(window_days - 1, 0))
    generated_at = utc_timestamp()
    source_errors: Dict[str, str] = {}

    connection = connect_database(state_path)
    try:
        _, source_errors = _collect_and_store_range(connection, config, start_date, end_date, generated_at)
        papers = load_all_papers(connection)
    finally:
        connection.close()

    export_outputs(papers, config, data_dir, generated_at, metadata={"source_errors": source_errors})


def run_backfill(config_path: str, state_path: str, data_dir: str, start_date: str, end_date: str) -> None:
    config = load_config(config_path)
    chunk_days = int(config["defaults"]["backfill_chunk_days"])
    generated_at = utc_timestamp()
    source_errors: Dict[str, str] = {}

    connection = connect_database(state_path)
    try:
        for chunk_start, chunk_end in chunk_date_ranges(parse_cli_date(start_date), parse_cli_date(end_date), chunk_days):
            _, chunk_errors = _collect_and_store_range(connection, config, chunk_start, chunk_end, generated_at)
            source_errors.update(chunk_errors)
        papers = load_all_papers(connection)
    finally:
        connection.close()

    export_outputs(papers, config, data_dir, generated_at, metadata={"source_errors": source_errors})


def run_export(config_path: str, state_path: str, data_dir: str) -> None:
    config = load_config(config_path)
    generated_at = utc_timestamp()
    connection = connect_database(state_path)
    try:
        papers = load_all_papers(connection)
    finally:
        connection.close()
    export_outputs(papers, config, data_dir, generated_at, metadata={"source_errors": {}})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Research Radar paper pipeline")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="Path to topics.yaml")
    parser.add_argument("--state-path", default=DEFAULT_STATE_PATH, help="Path to SQLite state file")
    parser.add_argument("--data-dir", default=DEFAULT_DATA_DIR, help="Output directory for exported JSON files")

    subparsers = parser.add_subparsers(dest="command", required=True)

    update_parser = subparsers.add_parser("update", help="Fetch a recent overlap window and export JSON")
    update_parser.add_argument("--days", type=int, default=None, help="Override the update window in days")

    backfill_parser = subparsers.add_parser("backfill", help="Fetch a historical range in chunks and export JSON")
    backfill_parser.add_argument("--start-date", required=True, help="Inclusive YYYY-MM-DD start date")
    backfill_parser.add_argument("--end-date", required=True, help="Inclusive YYYY-MM-DD end date")

    subparsers.add_parser("export", help="Rebuild JSON outputs from the SQLite store only")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config_path = str(Path(args.config))
    state_path = str(Path(args.state_path))
    data_dir = str(Path(args.data_dir))

    if args.command == "update":
        run_update(config_path, state_path, data_dir, days=args.days)
    elif args.command == "backfill":
        run_backfill(config_path, state_path, data_dir, args.start_date, args.end_date)
    elif args.command == "export":
        run_export(config_path, state_path, data_dir)
    else:
        parser.error(f"Unsupported command: {args.command}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
