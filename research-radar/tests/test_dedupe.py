import unittest

from research_radar.dedupe import deduplicate_papers
from research_radar.models import NormalizedPaper, PaperIdentifiers


FIRST_SEEN = "2026-03-14T00:00:00Z"


def make_paper(
    paper_key: str,
    title: str,
    authors,
    published_date: str,
    source_primary: str,
    doi: str = None,
    arxiv_id: str = None,
    pmid: str = None,
) -> NormalizedPaper:
    return NormalizedPaper(
        paper_key=paper_key,
        title=title,
        authors=list(authors),
        abstract="Test abstract",
        published_date=published_date,
        first_seen_at=FIRST_SEEN,
        source_primary=source_primary,
        sources=[source_primary],
        url=f"https://example.org/{paper_key}",
        identifiers=PaperIdentifiers(doi=doi, arxiv_id=arxiv_id, pmid=pmid),
        source_record_id=paper_key,
        source_url=f"https://example.org/{paper_key}",
    )


class DedupeTests(unittest.TestCase):
    def test_deduplicates_by_doi(self) -> None:
        papers = [
            make_paper("a", "Population genetics of recombination", ["Alice Example"], "2026-03-10", "biorxiv", doi="10.1000/test"),
            make_paper("b", "Population genetics of recombination", ["Alice Example"], "2026-03-10", "pubmed", doi="10.1000/test"),
        ]

        canonical = deduplicate_papers(papers)
        self.assertEqual(len(canonical), 1)
        self.assertEqual(sorted(canonical[0].sources), ["biorxiv", "pubmed"])

    def test_deduplicates_by_title_author_and_year_when_doi_missing(self) -> None:
        papers = [
            make_paper("a", "ARG inference in large populations", ["Alice Example"], "2026-03-10", "arxiv"),
            make_paper("b", "ARG inference in large populations", ["Alice Example"], "2026-01-05", "pubmed", pmid="123"),
        ]

        canonical = deduplicate_papers(papers)
        self.assertEqual(len(canonical), 1)
        self.assertEqual(canonical[0].identifiers.pmid, "123")

    def test_keeps_distinct_similar_titles(self) -> None:
        papers = [
            make_paper("a", "Population genetics of recombination", ["Alice Example"], "2026-03-10", "arxiv"),
            make_paper("b", "Population genetic models of recombination", ["Alice Example"], "2026-03-10", "pubmed"),
        ]

        canonical = deduplicate_papers(papers)
        self.assertEqual(len(canonical), 2)


if __name__ == "__main__":
    unittest.main()
