"""Tests for paper_discovery module."""

from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from models import ResearchInterests
from paper_discovery import PaperDiscoverer


@pytest.fixture
def discoverer() -> PaperDiscoverer:
    """Create paper discoverer."""
    return PaperDiscoverer()


@pytest.fixture
def sample_interests() -> ResearchInterests:
    """Create sample research interests."""
    return ResearchInterests(areas=["deep learning"], topics=["attention mechanisms"], arxiv_categories=["cs.LG"])


def test_build_query_with_all_fields(discoverer: PaperDiscoverer, sample_interests: ResearchInterests) -> None:
    """Test query building with all interest fields."""
    query = discoverer._build_query(sample_interests)

    # Should include category, topic
    assert "cat:cs.LG" in query
    assert "attention mechanisms" in query


def test_build_query_categories_only(discoverer: PaperDiscoverer) -> None:
    """Test query with only categories."""
    interests = ResearchInterests(areas=[], topics=[], arxiv_categories=["cs.LG", "eess.SP"])

    query = discoverer._build_query(interests)
    assert "cat:cs.LG" in query
    assert "cat:eess.SP" in query


def test_build_query_topics_only(discoverer: PaperDiscoverer) -> None:
    """Test query with only topics."""
    interests = ResearchInterests(areas=["deep learning"], topics=["attention", "transformers"], arxiv_categories=[])

    query = discoverer._build_query(interests)
    assert "attention" in query
    assert "transformers" in query


def test_build_query_areas_fallback(discoverer: PaperDiscoverer) -> None:
    """Test query uses areas when no topics."""
    interests = ResearchInterests(areas=["deep learning", "signal processing"], topics=[], arxiv_categories=[])

    query = discoverer._build_query(interests)
    assert "deep learning" in query
    assert "signal processing" in query


def test_build_query_empty(discoverer: PaperDiscoverer) -> None:
    """Test query with no interests returns all."""
    interests = ResearchInterests(areas=[], topics=[], arxiv_categories=[])

    query = discoverer._build_query(interests)
    assert query == "all:*"


@patch("paper_discovery.discoverer.arxiv.Client")
def test_discover_papers(
    mock_client_class: Mock, discoverer: PaperDiscoverer, sample_interests: ResearchInterests
) -> None:
    """Test discovering papers from arXiv."""
    # Mock arXiv result
    mock_result = Mock()
    mock_result.entry_id = "http://arxiv.org/abs/2301.12345"
    mock_result.title = "Test Paper"
    mock_result.authors = [Mock(name="Author One")]
    mock_result.summary = "Test abstract"
    mock_result.published = datetime.now()
    mock_result.categories = ["cs.LG"]

    # Setup mock client
    mock_client = Mock()
    mock_client.results.return_value = [mock_result]
    discoverer.client = mock_client

    # Discover papers
    papers = discoverer.discover(sample_interests, days=7, max_results=20)

    assert len(papers) == 1
    assert papers[0].id == "arxiv:2301.12345"
    assert papers[0].title == "Test Paper"
    assert papers[0].authors == ["Author One"]


@patch("paper_discovery.discoverer.arxiv.Client")
def test_get_by_id(mock_client_class: Mock, discoverer: PaperDiscoverer) -> None:
    """Test getting paper by arXiv ID."""
    # Mock arXiv result
    mock_result = Mock()
    mock_result.entry_id = "http://arxiv.org/abs/2301.12345"
    mock_result.title = "Test Paper"
    mock_result.authors = [Mock(name="Author One")]
    mock_result.summary = "Test abstract"
    mock_result.published = datetime.now()
    mock_result.categories = ["cs.LG"]

    # Setup mock client
    mock_client = Mock()
    mock_client.results.return_value = iter([mock_result])
    discoverer.client = mock_client

    # Get paper
    paper = discoverer.get_by_id("2301.12345")

    assert paper is not None
    assert paper.id == "arxiv:2301.12345"
    assert paper.title == "Test Paper"


@patch("paper_discovery.discoverer.arxiv.Client")
def test_get_by_id_not_found(mock_client_class: Mock, discoverer: PaperDiscoverer) -> None:
    """Test getting nonexistent paper returns None."""
    # Setup mock client with no results
    mock_client = Mock()
    mock_client.results.return_value = iter([])
    discoverer.client = mock_client

    # Get paper
    paper = discoverer.get_by_id("9999.99999")

    assert paper is None
