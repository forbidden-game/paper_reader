"""Paper storage and retrieval."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models import Paper


class PaperStore:
    """Manages paper collection storage.

    Papers stored as JSON files in .data/papers/<paper_id>.json
    """

    def __init__(self: PaperStore, data_dir: Path | None = None) -> None:
        """Initialize store.

        Args:
            data_dir: Base directory (default: .data/papers)
        """
        if data_dir is None:
            data_dir = Path.home() / ".data" / "papers"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def add(self: PaperStore, paper: Paper) -> None:
        """Add paper to collection.

        Args:
            paper: Paper to add

        Raises:
            ValueError: If paper already exists
        """
        path = self._get_paper_path(paper.id)
        if path.exists():
            raise ValueError(f"Paper {paper.id} already exists")

        self._save_paper(paper, path)

    def get(self: PaperStore, paper_id: str) -> Paper | None:
        """Get paper by ID.

        Args:
            paper_id: Paper identifier

        Returns:
            Paper if found, None otherwise
        """
        path = self._get_paper_path(paper_id)
        if not path.exists():
            return None

        return self._load_paper(path)

    def update(self: PaperStore, paper: Paper) -> None:
        """Update existing paper.

        Args:
            paper: Paper with updated data

        Raises:
            ValueError: If paper doesn't exist
        """
        path = self._get_paper_path(paper.id)
        if not path.exists():
            raise ValueError(f"Paper {paper.id} not found")

        self._save_paper(paper, path)

    def delete(self: PaperStore, paper_id: str) -> None:
        """Delete paper from collection.

        Args:
            paper_id: Paper identifier

        Raises:
            ValueError: If paper doesn't exist
        """
        path = self._get_paper_path(paper_id)
        if not path.exists():
            raise ValueError(f"Paper {paper_id} not found")

        path.unlink()

    def list_all(self: PaperStore) -> list[Paper]:
        """List all papers in collection.

        Returns:
            List of all papers
        """
        papers = []
        for path in self.data_dir.glob("*.json"):
            paper = self._load_paper(path)
            if paper:
                papers.append(paper)

        return papers

    def search(self: PaperStore, query: str) -> list[Paper]:
        """Search papers by text in title, abstract, or insights.

        Args:
            query: Search query (case-insensitive)

        Returns:
            List of matching papers
        """
        query_lower = query.lower()
        results = []

        for paper in self.list_all():
            if query_lower in paper.title.lower():
                results.append(paper)
                continue

            if hasattr(paper, "insights") and paper.insights:
                insights_text = (paper.insights.problem + paper.insights.method + paper.insights.key_results).lower()

                if query_lower in insights_text:
                    results.append(paper)

        return results

    def _get_paper_path(self: PaperStore, paper_id: str) -> Path:
        """Get path for paper JSON file."""
        safe_id = paper_id.replace(":", "_").replace("/", "_")
        return self.data_dir / f"{safe_id}.json"

    def _save_paper(self: PaperStore, paper: Paper, path: Path) -> None:
        """Save paper to JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(paper), f, indent=2, ensure_ascii=False)

    def _load_paper(self: PaperStore, path: Path) -> Paper | None:
        """Load paper from JSON file."""
        from models import Paper
        from models import PaperInsights

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            if "insights" in data and data["insights"]:
                data["insights"] = PaperInsights(**data["insights"])

            return Paper(**data)
        except Exception:
            return None
