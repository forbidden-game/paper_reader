"""Tests for paper_store module."""

import pytest
from models import Paper
from models import PaperInsights
from paper_store import PaperStore


@pytest.fixture
def temp_store(tmp_path):
    """Create temporary paper store."""
    return PaperStore(data_dir=tmp_path / "papers")


@pytest.fixture
def sample_paper():
    """Create sample paper."""
    return Paper(
        id="arxiv:2301.12345",
        title="Test Paper",
        authors=["Author One", "Author Two"],
        url="https://arxiv.org/abs/2301.12345",
        pdf_path=None,
        added_date="2025-10-31",
        interests=["deep learning"],
        insights=PaperInsights(
            problem="Test problem",
            method="Test method",
            key_results="Test results",
            contributions=["Contribution 1"],
            related_work=["Related 1"],
            future_directions=["Future 1"],
            classification="foundational",
        ),
        status="to-read",
        notes="",
    )


def test_add_paper(temp_store, sample_paper):
    """Test adding paper."""
    temp_store.add(sample_paper)

    retrieved = temp_store.get(sample_paper.id)
    assert retrieved is not None
    assert retrieved.id == sample_paper.id
    assert retrieved.title == sample_paper.title


def test_add_duplicate_paper(temp_store, sample_paper):
    """Test adding duplicate paper raises error."""
    temp_store.add(sample_paper)

    with pytest.raises(ValueError, match="already exists"):
        temp_store.add(sample_paper)


def test_get_nonexistent_paper(temp_store):
    """Test getting nonexistent paper returns None."""
    result = temp_store.get("nonexistent")
    assert result is None


def test_update_paper(temp_store, sample_paper):
    """Test updating paper."""
    temp_store.add(sample_paper)

    sample_paper.status = "read"
    sample_paper.notes = "Finished reading"
    temp_store.update(sample_paper)

    retrieved = temp_store.get(sample_paper.id)
    assert retrieved.status == "read"
    assert retrieved.notes == "Finished reading"


def test_update_nonexistent_paper(temp_store, sample_paper):
    """Test updating nonexistent paper raises error."""
    with pytest.raises(ValueError, match="not found"):
        temp_store.update(sample_paper)


def test_delete_paper(temp_store, sample_paper):
    """Test deleting paper."""
    temp_store.add(sample_paper)
    temp_store.delete(sample_paper.id)

    assert temp_store.get(sample_paper.id) is None


def test_delete_nonexistent_paper(temp_store):
    """Test deleting nonexistent paper raises error."""
    with pytest.raises(ValueError, match="not found"):
        temp_store.delete("nonexistent")


def test_list_all_papers(temp_store, sample_paper):
    """Test listing all papers."""
    temp_store.add(sample_paper)

    paper2 = Paper(
        id="arxiv:2301.67890",
        title="Second Paper",
        authors=["Author Three"],
        url="https://arxiv.org/abs/2301.67890",
        pdf_path=None,
        added_date="2025-10-31",
        interests=["signal processing"],
        insights=PaperInsights(
            problem="Test problem 2",
            method="Test method 2",
            key_results="Test results 2",
            contributions=["Contribution 2"],
            related_work=["Related 2"],
            future_directions=["Future 2"],
            classification="incremental",
        ),
        status="to-read",
        notes="",
    )
    temp_store.add(paper2)

    papers = temp_store.list_all()
    assert len(papers) == 2
    assert any(p.id == sample_paper.id for p in papers)
    assert any(p.id == paper2.id for p in papers)


def test_search_by_title(temp_store, sample_paper):
    """Test searching by title."""
    temp_store.add(sample_paper)

    results = temp_store.search("Test Paper")
    assert len(results) == 1
    assert results[0].id == sample_paper.id


def test_search_by_insights(temp_store, sample_paper):
    """Test searching by insights content."""
    temp_store.add(sample_paper)

    results = temp_store.search("Test method")
    assert len(results) == 1
    assert results[0].id == sample_paper.id


def test_search_case_insensitive(temp_store, sample_paper):
    """Test search is case-insensitive."""
    temp_store.add(sample_paper)

    results = temp_store.search("test paper")
    assert len(results) == 1
