"""Data models for paper_reader."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Literal


@dataclass
class ResearchInterests:
    """User's research interests for paper discovery.

    Attributes:
        areas: Research areas (e.g., ["deep learning", "signal processing"])
        topics: Specific topics (e.g., ["attention mechanisms", "MIMO"])
        arxiv_categories: arXiv categories (e.g., ["cs.LG", "eess.SP"])
    """

    areas: list[str]
    topics: list[str]
    arxiv_categories: list[str] = field(default_factory=list)


@dataclass
class PaperCandidate:
    """Paper discovered from arXiv but not yet added to collection.

    Attributes:
        id: Unique identifier (e.g., "arxiv:2301.12345")
        title: Paper title
        authors: List of author names
        abstract: Paper abstract
        url: URL to paper (arXiv or PDF)
        published_date: Publication date (ISO format)
        arxiv_categories: arXiv categories (e.g., ["cs.LG"])
    """

    id: str
    title: str
    authors: list[str]
    abstract: str
    url: str
    published_date: str
    arxiv_categories: list[str]


@dataclass
class PaperInsights:
    """Extracted insights from paper analysis.

    Attributes:
        problem: What problem does this paper address?
        method: What approach/method does it use?
        key_results: Main findings/results
        contributions: Key contributions (list)
        related_work: Papers mentioned in related work (list)
        future_directions: Suggested future work (list)
        classification: Is this foundational or incremental research?
    """

    problem: str
    method: str
    key_results: str
    contributions: list[str]
    related_work: list[str]
    future_directions: list[str]
    classification: Literal["foundational", "incremental"]


@dataclass
class Paper:
    """Paper in user's collection with extracted insights.

    Attributes:
        id: Unique identifier (e.g., "arxiv:2301.12345")
        title: Paper title
        authors: List of author names
        url: URL to paper
        pdf_path: Path to downloaded/local PDF (if available)
        added_date: When paper was added to collection (ISO format)
        interests: Research areas/topics this paper relates to
        insights: Extracted structured insights
        status: Reading status
        notes: User's personal notes
    """

    id: str
    title: str
    authors: list[str]
    url: str
    pdf_path: str | None
    added_date: str
    interests: list[str]
    insights: PaperInsights
    status: Literal["to-read", "reading", "read"]
    notes: str = ""
