import json
from pathlib import Path
from xml.etree import ElementTree as ET
import unittest

from research_radar.normalize import ARXIV_NS, normalize_biorxiv_item, parse_arxiv_entry, parse_pubmed_article


FIXTURES = Path(__file__).resolve().parent / "fixtures"
FIRST_SEEN = "2026-03-14T00:00:00Z"


class NormalizeTests(unittest.TestCase):
    def test_biorxiv_normalization(self) -> None:
        item = json.loads((FIXTURES / "biorxiv_item.json").read_text(encoding="utf-8"))
        paper = normalize_biorxiv_item(item, FIRST_SEEN)

        self.assertEqual(paper.title, "An ancestral recombination graph view of population genetics")
        self.assertEqual(paper.authors, ["Alice Example", "Bob Example"])
        self.assertEqual(paper.published_date, "2026-03-10")
        self.assertEqual(paper.source_primary, "biorxiv")
        self.assertEqual(paper.venue, "bioRxiv")
        self.assertEqual(paper.identifiers.biorxiv_doi, "10.1101/2026.03.10.123456")
        self.assertEqual(paper.identifiers.doi, "10.1038/s41586-026-12345-6")

    def test_arxiv_normalization(self) -> None:
        root = ET.fromstring((FIXTURES / "arxiv_feed.xml").read_text(encoding="utf-8"))
        entry = root.find("atom:entry", ARXIV_NS)
        self.assertIsNotNone(entry)
        paper = parse_arxiv_entry(entry, FIRST_SEEN)  # type: ignore[arg-type]

        self.assertEqual(paper.title, "Pangenome graphs for structural variation discovery")
        self.assertEqual(paper.authors, ["Carol Example", "Dan Example"])
        self.assertEqual(paper.published_date, "2026-03-11")
        self.assertEqual(paper.venue, "arXiv")
        self.assertEqual(paper.identifiers.arxiv_id, "2603.12345")
        self.assertEqual(paper.identifiers.doi, "10.48550/arxiv.2603.12345")

    def test_pubmed_normalization(self) -> None:
        root = ET.fromstring((FIXTURES / "pubmed_article.xml").read_text(encoding="utf-8"))
        article = root.find(".//PubmedArticle")
        self.assertIsNotNone(article)
        paper = parse_pubmed_article(article, FIRST_SEEN)  # type: ignore[arg-type]

        self.assertEqual(paper.title, "Phylogenomics and phylodynamics in rapidly evolving pathogens")
        self.assertEqual(paper.authors, ["Eve Example", "Frank Example"])
        self.assertEqual(paper.published_date, "2026-03-12")
        self.assertEqual(paper.venue, "Mol Biol Evol")
        self.assertEqual(paper.identifiers.pmid, "12345678")
        self.assertEqual(paper.identifiers.pmcid, "PMC1234567")


if __name__ == "__main__":
    unittest.main()
