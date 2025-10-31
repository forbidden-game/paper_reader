"""Tests for paper_ingestor module."""

from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from models import PaperCandidate
from paper_ingestor import PaperIngestor


@pytest.fixture
def temp_ingestor(tmp_path: Path) -> PaperIngestor:
    """Create temporary paper ingestor."""
    return PaperIngestor(pdf_dir=tmp_path / "pdfs")


@pytest.fixture
def sample_candidate() -> PaperCandidate:
    """Create sample paper candidate."""
    return PaperCandidate(
        id="arxiv:2301.12345",
        title="Test Paper",
        authors=["Author One"],
        abstract="Test abstract",
        url="https://arxiv.org/abs/2301.12345",
        published_date="2025-10-31",
        arxiv_categories=["cs.LG"],
    )


def test_ingestor_creates_pdf_dir(tmp_path: Path) -> None:
    """Test ingestor creates PDF directory."""
    pdf_dir = tmp_path / "pdfs"
    assert not pdf_dir.exists()

    PaperIngestor(pdf_dir=pdf_dir)

    assert pdf_dir.exists()


@patch("paper_ingestor.ingestor.arxiv.Client")
def test_download_pdf(mock_client_class: Mock, temp_ingestor: PaperIngestor) -> None:
    """Test downloading PDF from arXiv."""
    # Mock arXiv result
    mock_result = Mock()
    mock_result.download_pdf = Mock()

    # Setup mock client
    mock_client = Mock()
    mock_client.results.return_value = iter([mock_result])
    temp_ingestor.client = mock_client

    # Download
    pdf_path = temp_ingestor._download_pdf("2301.12345")

    assert pdf_path.name == "2301.12345.pdf"
    mock_result.download_pdf.assert_called_once()


@patch("paper_ingestor.ingestor.arxiv.Client")
def test_download_pdf_not_found(mock_client_class: Mock, temp_ingestor: PaperIngestor) -> None:
    """Test downloading nonexistent paper raises error."""
    # Setup mock client with no results
    mock_client = Mock()
    mock_client.results.return_value = iter([])
    temp_ingestor.client = mock_client

    with pytest.raises(ValueError, match="not found"):
        temp_ingestor._download_pdf("9999.99999")


def test_extract_text(temp_ingestor: PaperIngestor, tmp_path: Path) -> None:
    """Test extracting text from PDF."""
    # Create mock PDF
    pdf_path = tmp_path / "test.pdf"

    # Mock PdfReader
    with patch("paper_ingestor.ingestor.PdfReader") as mock_reader_class:
        mock_page = Mock()
        mock_page.extract_text.return_value = "Test content"

        mock_reader = Mock()
        mock_reader.pages = [mock_page]
        mock_reader_class.return_value = mock_reader

        # Create dummy file
        pdf_path.write_bytes(b"dummy pdf")

        text = temp_ingestor._extract_text(pdf_path)

        assert text == "Test content"


def test_extract_text_empty(temp_ingestor: PaperIngestor, tmp_path: Path) -> None:
    """Test extracting from empty PDF raises error."""
    pdf_path = tmp_path / "test.pdf"

    # Mock PdfReader with empty content
    with patch("paper_ingestor.ingestor.PdfReader") as mock_reader_class:
        mock_page = Mock()
        mock_page.extract_text.return_value = ""

        mock_reader = Mock()
        mock_reader.pages = [mock_page]
        mock_reader_class.return_value = mock_reader

        # Create dummy file
        pdf_path.write_bytes(b"dummy pdf")

        with pytest.raises(ValueError, match="No text extracted"):
            temp_ingestor._extract_text(pdf_path)


def test_ingest_from_local_not_found(temp_ingestor: PaperIngestor, tmp_path: Path) -> None:
    """Test ingesting from nonexistent local file raises error."""
    pdf_path = tmp_path / "nonexistent.pdf"

    with pytest.raises(FileNotFoundError):
        temp_ingestor.ingest_from_local(pdf_path)


@patch("paper_ingestor.ingestor.arxiv.Client")
@patch("paper_ingestor.ingestor.PdfReader")
def test_ingest_from_arxiv(
    mock_reader_class: Mock,
    mock_client_class: Mock,
    temp_ingestor: PaperIngestor,
    sample_candidate: PaperCandidate,
) -> None:
    """Test full ingestion from arXiv."""
    # Mock arXiv download
    mock_result = Mock()
    mock_result.download_pdf = Mock()

    mock_client = Mock()
    mock_client.results.return_value = iter([mock_result])
    temp_ingestor.client = mock_client

    # Mock PDF reading
    mock_page = Mock()
    mock_page.extract_text.return_value = "Paper content"

    mock_reader = Mock()
    mock_reader.pages = [mock_page]
    mock_reader_class.return_value = mock_reader

    # Ingest
    pdf_path, text = temp_ingestor.ingest_from_arxiv(sample_candidate)

    assert "2301.12345.pdf" in pdf_path
    assert text == "Paper content"
