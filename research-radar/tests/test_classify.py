import unittest

from research_radar.classify import classify_paper
from research_radar.models import NormalizedPaper, PaperIdentifiers


TOPICS = {
    "mutation_rate": {
        "priority": 10,
        "include_phrases": ["mutation rate", "mutation rates", "de novo mutation rate", "mutation accumulation"],
        "include_aliases": [],
        "require_any_phrases": ["germline", "de novo", "pedigree", "genome", "genomic", "evolution"],
        "exclude_phrases": [],
    },
    "arg": {
        "priority": 20,
        "include_phrases": ["ancestral recombination graph", "sequentially markov coalescent"],
        "include_aliases": ["argweaver"],
        "require_any_phrases": [],
        "exclude_phrases": [],
    },
    "pangenome": {
        "priority": 30,
        "include_phrases": ["pangenome", "variation graph", "graph genome"],
        "include_aliases": [],
        "require_any_phrases": [],
        "exclude_phrases": [],
    },
    "other": {
        "priority": 999,
        "include_phrases": [],
        "include_aliases": [],
        "require_any_phrases": [],
        "exclude_phrases": [],
    },
}


def make_paper(title: str, abstract: str) -> NormalizedPaper:
    return NormalizedPaper(
        paper_key="test",
        title=title,
        authors=["Alice Example"],
        abstract=abstract,
        published_date="2026-03-10",
        first_seen_at="2026-03-14T00:00:00Z",
        source_primary="arxiv",
        sources=["arxiv"],
        url="https://example.org/test",
        identifiers=PaperIdentifiers(arxiv_id="2603.12345"),
    )


class ClassifyTests(unittest.TestCase):
    def test_title_hits_determine_primary_topic(self) -> None:
        paper = make_paper(
            "Ancestral recombination graph inference for long haplotypes",
            "A benchmarking study.",
        )

        classify_paper(paper, TOPICS)
        self.assertEqual(paper.primary_topic, "arg")
        self.assertEqual(paper.topics[:1], ["arg"])

    def test_abstract_only_hit_is_detected(self) -> None:
        paper = make_paper(
            "A new inference pipeline",
            "We estimate mutation rates across pedigrees and compare de novo mutation rate shifts.",
        )

        classify_paper(paper, TOPICS)
        self.assertEqual(paper.primary_topic, "mutation_rate")

    def test_required_context_filters_generic_hits(self) -> None:
        paper = make_paper(
            "A survey of viral dynamics",
            "The marker has a high mutation rate across samples, but the study is focused on assay performance only.",
        )

        classify_paper(paper, TOPICS)
        self.assertEqual(paper.primary_topic, "other")

    def test_multiple_topics_have_deterministic_priority(self) -> None:
        paper = make_paper(
            "Pangenome resources for ancestral recombination graph analysis",
            "Variation graph approaches are compared to ancestral recombination graph methods.",
        )

        classify_paper(paper, TOPICS)
        self.assertEqual(paper.topics[:2], ["pangenome", "arg"])
        self.assertEqual(paper.primary_topic, "pangenome")

    def test_other_is_used_when_no_rules_match(self) -> None:
        paper = make_paper("Completely unrelated title", "No relevant abstract terms.")

        classify_paper(paper, TOPICS)
        self.assertEqual(paper.primary_topic, "other")
        self.assertEqual(paper.topics, ["other"])


if __name__ == "__main__":
    unittest.main()
