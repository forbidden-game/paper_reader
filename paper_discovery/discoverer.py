"""Paper discovery from arXiv."""

from __future__ import annotations

from datetime import UTC
from datetime import datetime
from datetime import timedelta
from typing import TYPE_CHECKING

import arxiv

if TYPE_CHECKING:
    from models import PaperCandidate
    from models import ResearchInterests


class PaperDiscoverer:
    """Discovers papers from arXiv based on research interests."""

    def __init__(self) -> None:
        """Initialize discoverer."""
        self.client = arxiv.Client()

    def discover(self, interests: ResearchInterests, days: int = 7, max_results: int = 20) -> list[PaperCandidate]:
        """Discover papers from arXiv.

        Args:
            interests: Research interests to search for
            days: Number of days to look back (default: 7)
            max_results: Maximum results per query (default: 20)

        Returns:
            List of discovered paper candidates
        """
        from models import PaperCandidate

        # Build search query
        query = self._build_query(interests)

        # Calculate date range
        end_date = datetime.now(UTC)
        start_date = end_date - timedelta(days=days)

        # Search arXiv
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

        # Convert results to PaperCandidate
        candidates = []
        for result in self.client.results(search):
            # Filter by date
            if result.published < start_date:
                continue

            candidate = PaperCandidate(
                id=f"arxiv:{result.entry_id.split('/')[-1]}",
                title=result.title,
                authors=[author.name for author in result.authors],
                abstract=result.summary,
                url=result.entry_id,
                published_date=result.published.isoformat(),
                arxiv_categories=result.categories,
            )
            candidates.append(candidate)

        return candidates

    def _build_query(self, interests: ResearchInterests) -> str:
        """Build arXiv search query from interests.

        Args:
            interests: Research interests

        Returns:
            arXiv search query string
        """
        query_parts = []

        # Add categories if specified
        if interests.arxiv_categories:
            cat_queries = [f"cat:{cat}" for cat in interests.arxiv_categories]
            query_parts.append("(" + " OR ".join(cat_queries) + ")")

        # Add topics (search in title and abstract)
        if interests.topics:
            topic_queries = []
            for topic in interests.topics:
                topic_queries.append(f'(ti:"{topic}" OR abs:"{topic}")')
            query_parts.append("(" + " OR ".join(topic_queries) + ")")

        # Add areas if no topics specified
        elif interests.areas:
            area_queries = []
            for area in interests.areas:
                area_queries.append(f'(ti:"{area}" OR abs:"{area}")')
            query_parts.append("(" + " OR ".join(area_queries) + ")")

        # Combine with AND
        if not query_parts:
            return "all:*"  # Return all if no criteria

        return " AND ".join(query_parts)

    def get_by_id(self, arxiv_id: str) -> PaperCandidate | None:
        """Get specific paper by arXiv ID.

        Args:
            arxiv_id: arXiv ID (e.g., "2301.12345" or "arxiv:2301.12345")

        Returns:
            PaperCandidate if found, None otherwise
        """
        from models import PaperCandidate

        # Clean ID
        clean_id = arxiv_id.replace("arxiv:", "")

        # Search by ID
        search = arxiv.Search(id_list=[clean_id])

        try:
            result = next(self.client.results(search))

            return PaperCandidate(
                id=f"arxiv:{result.entry_id.split('/')[-1]}",
                title=result.title,
                authors=[author.name for author in result.authors],
                abstract=result.summary,
                url=result.entry_id,
                published_date=result.published.isoformat(),
                arxiv_categories=result.categories,
            )
        except StopIteration:
            return None
