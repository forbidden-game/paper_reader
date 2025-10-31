"""Tests for interest_manager module."""

import pytest
from interest_manager import InterestManager
from models import ResearchInterests


@pytest.fixture
def temp_manager(tmp_path):
    """Create temporary interest manager."""
    return InterestManager(data_dir=tmp_path / "paper_reader")


def test_load_nonexistent(temp_manager):
    """Test loading when no interests file exists."""
    result = temp_manager.load()
    assert result is None


def test_save_and_load(temp_manager):
    """Test saving and loading interests."""
    interests = ResearchInterests(
        areas=["deep learning", "signal processing"],
        topics=["attention mechanisms", "MIMO"],
        arxiv_categories=["cs.LG", "eess.SP"],
    )

    temp_manager.save(interests)
    loaded = temp_manager.load()

    assert loaded is not None
    assert loaded.areas == interests.areas
    assert loaded.topics == interests.topics
    assert loaded.arxiv_categories == interests.arxiv_categories


def test_add_area(temp_manager):
    """Test adding research area."""
    temp_manager.add_area("deep learning")

    interests = temp_manager.load()
    assert interests is not None
    assert "deep learning" in interests.areas


def test_add_area_duplicate(temp_manager):
    """Test adding duplicate area doesn't create duplicates."""
    temp_manager.add_area("deep learning")
    temp_manager.add_area("deep learning")

    interests = temp_manager.load()
    assert interests.areas.count("deep learning") == 1


def test_add_topic(temp_manager):
    """Test adding topic."""
    temp_manager.add_topic("attention mechanisms")

    interests = temp_manager.load()
    assert interests is not None
    assert "attention mechanisms" in interests.topics


def test_add_category(temp_manager):
    """Test adding arXiv category."""
    temp_manager.add_category("cs.LG")

    interests = temp_manager.load()
    assert interests is not None
    assert "cs.LG" in interests.arxiv_categories


def test_remove_area(temp_manager):
    """Test removing area."""
    temp_manager.add_area("deep learning")
    temp_manager.add_area("signal processing")
    temp_manager.remove_area("deep learning")

    interests = temp_manager.load()
    assert "deep learning" not in interests.areas
    assert "signal processing" in interests.areas


def test_remove_topic(temp_manager):
    """Test removing topic."""
    temp_manager.add_topic("attention")
    temp_manager.add_topic("MIMO")
    temp_manager.remove_topic("attention")

    interests = temp_manager.load()
    assert "attention" not in interests.topics
    assert "MIMO" in interests.topics


def test_remove_category(temp_manager):
    """Test removing category."""
    temp_manager.add_category("cs.LG")
    temp_manager.add_category("eess.SP")
    temp_manager.remove_category("cs.LG")

    interests = temp_manager.load()
    assert "cs.LG" not in interests.arxiv_categories
    assert "eess.SP" in interests.arxiv_categories


def test_remove_nonexistent(temp_manager):
    """Test removing nonexistent item does nothing."""
    # Should not raise error
    temp_manager.remove_area("nonexistent")
    temp_manager.remove_topic("nonexistent")
    temp_manager.remove_category("nonexistent")
