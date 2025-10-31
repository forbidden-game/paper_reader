"""Research interest management."""

from __future__ import annotations

import json
from pathlib import Path

from models import ResearchInterests


class InterestManager:
    """Manages user's research interests.

    Interests stored in .data/paper_reader/interests.json
    """

    def __init__(self, data_dir: Path | None = None):
        """Initialize manager.

        Args:
            data_dir: Base directory (default: .data/paper_reader)
        """
        if data_dir is None:
            data_dir = Path.home() / ".data" / "paper_reader"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.interests_file = self.data_dir / "interests.json"

    def load(self) -> ResearchInterests | None:
        """Load interests from file.

        Returns:
            ResearchInterests if file exists, None otherwise
        """
        if not self.interests_file.exists():
            return None

        try:
            with open(self.interests_file, encoding="utf-8") as f:
                data = json.load(f)
            return ResearchInterests(**data)
        except Exception:
            return None

    def save(self, interests: ResearchInterests) -> None:
        """Save interests to file.

        Args:
            interests: Research interests to save
        """
        from dataclasses import asdict

        with open(self.interests_file, "w", encoding="utf-8") as f:
            json.dump(asdict(interests), f, indent=2, ensure_ascii=False)

    def add_area(self, area: str) -> None:
        """Add research area.

        Args:
            area: Research area to add
        """
        interests = self.load() or ResearchInterests(areas=[], topics=[], arxiv_categories=[])
        if area not in interests.areas:
            interests.areas.append(area)
            self.save(interests)

    def add_topic(self, topic: str) -> None:
        """Add specific topic.

        Args:
            topic: Topic to add
        """
        interests = self.load() or ResearchInterests(areas=[], topics=[], arxiv_categories=[])
        if topic not in interests.topics:
            interests.topics.append(topic)
            self.save(interests)

    def add_category(self, category: str) -> None:
        """Add arXiv category.

        Args:
            category: arXiv category (e.g., "cs.LG")
        """
        interests = self.load() or ResearchInterests(areas=[], topics=[], arxiv_categories=[])
        if category not in interests.arxiv_categories:
            interests.arxiv_categories.append(category)
            self.save(interests)

    def remove_area(self, area: str) -> None:
        """Remove research area.

        Args:
            area: Research area to remove
        """
        interests = self.load()
        if interests and area in interests.areas:
            interests.areas.remove(area)
            self.save(interests)

    def remove_topic(self, topic: str) -> None:
        """Remove topic.

        Args:
            topic: Topic to remove
        """
        interests = self.load()
        if interests and topic in interests.topics:
            interests.topics.remove(topic)
            self.save(interests)

    def remove_category(self, category: str) -> None:
        """Remove arXiv category.

        Args:
            category: Category to remove
        """
        interests = self.load()
        if interests and category in interests.arxiv_categories:
            interests.arxiv_categories.remove(category)
            self.save(interests)
