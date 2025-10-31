"""Tests for insight_extractor module."""

from unittest.mock import Mock
from unittest.mock import patch

import pytest
from insight_extractor import InsightExtractor


@pytest.fixture
def extractor():
    """Create insight extractor."""
    return InsightExtractor()


@pytest.fixture
def sample_paper_text():
    """Sample paper text."""
    return """
    Abstract: We propose a novel attention mechanism...

    1. Introduction
    The problem of efficient attention has been widely studied...

    2. Method
    Our approach uses sparse attention patterns...

    3. Results
    We achieve 95% accuracy on benchmark datasets...

    4. Conclusion
    This work demonstrates the effectiveness of sparse attention...
    """


def test_build_extraction_prompt(extractor, sample_paper_text):
    """Test building extraction prompt."""
    prompt = extractor._build_extraction_prompt(title="Sparse Attention Mechanisms", text=sample_paper_text)

    assert "Sparse Attention Mechanisms" in prompt
    assert "PROBLEM" in prompt
    assert "METHOD" in prompt
    assert "JSON" in prompt


def test_build_extraction_prompt_truncates_long_text(extractor):
    """Test prompt truncates very long text."""
    long_text = "x" * 10000

    prompt = extractor._build_extraction_prompt(title="Test Paper", text=long_text)

    assert "truncated" in prompt
    assert len(prompt) < len(long_text)


def test_parse_response_with_json(extractor):
    """Test parsing response with JSON."""
    response = """{
        "problem": "Test problem",
        "method": "Test method",
        "key_results": "Test results",
        "contributions": ["Contribution 1"],
        "related_work": ["Related 1"],
        "future_directions": ["Future 1"],
        "classification": "foundational"
    }"""

    insights = extractor._parse_response(response)

    assert insights.problem == "Test problem"
    assert insights.method == "Test method"
    assert insights.classification == "foundational"


def test_parse_response_with_markdown_wrapper(extractor):
    """Test parsing response with markdown code block."""
    response = """```json
    {
        "problem": "Test problem",
        "method": "Test method",
        "key_results": "Test results",
        "contributions": ["Contribution 1"],
        "related_work": ["Related 1"],
        "future_directions": ["Future 1"],
        "classification": "incremental"
    }
    ```"""

    insights = extractor._parse_response(response)

    assert insights.problem == "Test problem"
    assert insights.classification == "incremental"


def test_parse_response_invalid_json(extractor):
    """Test parsing invalid JSON raises error."""
    response = "This is not JSON"

    with pytest.raises(ValueError, match="Failed to parse"):
        extractor._parse_response(response)


@patch("insight_extractor.extractor.ClaudeCode")
def test_extract(mock_claude_class, extractor, sample_paper_text):
    """Test full extraction workflow."""
    # Mock Claude response
    mock_response = """{
        "problem": "Efficient attention mechanisms",
        "method": "Sparse attention patterns",
        "key_results": "95% accuracy",
        "contributions": ["Novel sparse attention"],
        "related_work": ["Transformer papers"],
        "future_directions": ["Further optimization"],
        "classification": "foundational"
    }"""

    mock_claude = Mock()
    mock_claude.generate.return_value = mock_response
    mock_claude_class.return_value = mock_claude

    # Extract insights
    insights = extractor.extract(paper_text=sample_paper_text, paper_title="Sparse Attention")

    assert insights.problem == "Efficient attention mechanisms"
    assert insights.method == "Sparse attention patterns"
    assert insights.classification == "foundational"
