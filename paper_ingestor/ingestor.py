"""Paper ingestion and PDF text extraction."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import arxiv
from pypdf import PdfReader

if TYPE_CHECKING:
    from models import PaperCandidate


class PaperIngestor:
    """Ingests papers and extracts text content."""

    def __init__(self: PaperIngestor, pdf_dir: Path | None = None) -> None:
        """Initialize ingestor.

        Args:
            pdf_dir: Directory for storing PDFs (default: .data/papers/pdfs)
        """
        if pdf_dir is None:
            pdf_dir = Path.home() / ".data" / "papers" / "pdfs"
        self.pdf_dir = pdf_dir
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
        self.client = arxiv.Client()

    def ingest_from_arxiv(self: PaperIngestor, candidate: PaperCandidate) -> tuple[str, str]:
        """Ingest paper from arXiv.

        Downloads PDF and extracts text.

        Args:
            candidate: Paper candidate with arXiv ID

        Returns:
            Tuple of (pdf_path, extracted_text)

        Raises:
            ValueError: If paper cannot be downloaded
        """
        # Get clean arXiv ID
        arxiv_id = candidate.id.replace("arxiv:", "")

        # Download PDF
        pdf_path = self._download_pdf(arxiv_id)

        # Extract text
        text = self._extract_text(pdf_path)

        return str(pdf_path), text

    def ingest_from_local(self: PaperIngestor, pdf_path: Path) -> str:
        """Ingest paper from local PDF file.

        Args:
            pdf_path: Path to local PDF

        Returns:
            Extracted text

        Raises:
            FileNotFoundError: If PDF doesn't exist
            ValueError: If text extraction fails
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        return self._extract_text(pdf_path)

    def _download_pdf(self: PaperIngestor, arxiv_id: str) -> Path:
        """Download PDF from arXiv.

        Args:
            arxiv_id: arXiv ID (without prefix)

        Returns:
            Path to downloaded PDF

        Raises:
            ValueError: If download fails
        """
        # Search for paper
        search = arxiv.Search(id_list=[arxiv_id])

        try:
            result = next(self.client.results(search))
        except StopIteration:
            raise ValueError(f"Paper {arxiv_id} not found on arXiv")

        # Download PDF
        pdf_path = self.pdf_dir / f"{arxiv_id}.pdf"
        result.download_pdf(filename=str(pdf_path))

        return pdf_path

    def _extract_text(self: PaperIngestor, pdf_path: Path) -> str:
        """Extract text from PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text

        Raises:
            ValueError: If extraction fails
        """
        try:
            reader = PdfReader(pdf_path)

            # Extract text from all pages
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            full_text = "\n\n".join(text_parts)

            if not full_text.strip():
                raise ValueError("No text extracted from PDF")

            return full_text

        except Exception as e:
            raise ValueError(f"Failed to extract text: {e}")
