import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from research_radar.export import export_outputs
from research_radar.models import NormalizedPaper, PaperIdentifiers


CONFIG = {
    "paper_watch": {
        "topic_ids": ["mutation_rate", "arg", "pangenome"],
        "minimum_per_topic": 2,
    },
    "exports": {
        "recent_limit": 10,
    },
    "topics": {
        "mutation_rate": {
            "label": "Mutation Rate",
            "priority": 10,
            "include_phrases": ["mutation rate"],
            "include_aliases": [],
            "exclude_phrases": [],
        },
        "arg": {
            "label": "Ancestral Recombination Graph",
            "priority": 20,
            "include_phrases": ["ancestral recombination graph"],
            "include_aliases": [],
            "exclude_phrases": [],
        },
        "pangenome": {
            "label": "Pangenome",
            "priority": 30,
            "include_phrases": ["pangenome"],
            "include_aliases": [],
            "exclude_phrases": [],
        },
        "other": {"label": "Other"},
    },
}


def make_paper(title: str, published_date: str, topic: str) -> NormalizedPaper:
    if topic == "mutation_rate":
        abstract = "We estimate the de novo mutation rate in a pedigree study."
    elif topic == "arg":
        abstract = "This method infers the ancestral recombination graph from tree sequence data."
    elif topic == "pangenome":
        abstract = "We compare pangenome graph resources across isolates."
    else:
        abstract = "Population genetics methods."
    return NormalizedPaper(
        paper_key=f"title:{published_date}",
        title=title,
        authors=["Alice Example"],
        abstract=abstract,
        published_date=published_date,
        first_seen_at="2026-03-14T00:00:00Z",
        source_primary="pubmed",
        sources=["pubmed"],
        url="https://example.org/paper",
        venue="Genome Research",
        identifiers=PaperIdentifiers(pmid="1"),
        topics=[topic],
        primary_topic=topic,
        matched_keywords={topic: ["population genetics"]} if topic != "other" else {},
    )


class ExportTests(unittest.TestCase):
    def test_export_outputs_writes_required_files(self) -> None:
        papers = [
            make_paper("Pedigree mutation rate estimate", "2026-03-10", "mutation_rate"),
            make_paper("Paper B", "2026-02-10", "other"),
        ]
        with TemporaryDirectory() as tmpdir:
            export_outputs(papers, CONFIG, tmpdir, "2026-03-14T00:00:00Z")

            expected = [
                "recent_papers.json",
                "summary.json",
            ]
            for filename in expected:
                payload = json.loads((Path(tmpdir) / filename).read_text(encoding="utf-8"))
                self.assertTrue(payload)

            recent_payload = json.loads((Path(tmpdir) / "recent_papers.json").read_text(encoding="utf-8"))
            self.assertEqual(len(recent_payload["latest"]), 1)
            self.assertEqual(recent_payload["latest"][0]["primary_topic"], "mutation_rate")
            self.assertEqual(recent_payload["latest"][0]["venue_display"], "Genome Research")

    def test_export_keeps_minimum_per_topic_when_available(self) -> None:
        papers = [
            make_paper("Mutation paper 1", "2026-03-10", "mutation_rate"),
            make_paper("Mutation paper 2", "2026-03-09", "mutation_rate"),
            make_paper("Mutation paper 3", "2026-03-08", "mutation_rate"),
            make_paper("ARG paper 1", "2026-03-11", "arg"),
            make_paper("ARG paper 2", "2026-03-07", "arg"),
            make_paper("ARG paper 3", "2026-03-06", "arg"),
            make_paper("Pangenome paper 1", "2026-03-05", "pangenome"),
        ]

        with TemporaryDirectory() as tmpdir:
            export_outputs(papers, CONFIG, tmpdir, "2026-03-14T00:00:00Z")
            recent_payload = json.loads((Path(tmpdir) / "recent_papers.json").read_text(encoding="utf-8"))
            topics = [paper["primary_topic"] for paper in recent_payload["latest"]]
            self.assertGreaterEqual(topics.count("mutation_rate"), 2)
            self.assertGreaterEqual(topics.count("arg"), 2)


if __name__ == "__main__":
    unittest.main()
