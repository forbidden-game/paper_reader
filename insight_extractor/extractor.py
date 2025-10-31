"""AI-powered insight extraction using Claude Code SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models import PaperInsights


class InsightExtractor:
    """Extracts structured insights from paper text using Claude."""

    def __init__(self):
        """Initialize extractor."""

    def extract(self, paper_text: str, paper_title: str) -> PaperInsights:
        """Extract insights from paper text.

        Uses Claude Code SDK to analyze paper and extract:
        - Problem being addressed
        - Method/approach used
        - Key results
        - Contributions
        - Related work references
        - Future directions
        - Classification (foundational vs incremental)

        Args:
            paper_text: Full text of paper
            paper_title: Title of paper

        Returns:
            PaperInsights with extracted information

        Raises:
            ValueError: If extraction fails
        """
        from claude_code import ClaudeCode

        # Build prompt for Claude
        prompt = self._build_extraction_prompt(paper_title, paper_text)

        try:
            # Use Claude Code SDK to extract insights
            claude = ClaudeCode()
            response = claude.generate(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.2,  # Lower temperature for more focused extraction
            )

            # Parse response into PaperInsights
            insights = self._parse_response(response)

            return insights

        except Exception as e:
            raise ValueError(f"Failed to extract insights: {e}")

    def _build_extraction_prompt(self, title: str, text: str) -> str:
        """Build prompt for Claude to extract insights.

        Args:
            title: Paper title
            text: Paper text

        Returns:
            Formatted prompt
        """
        # Truncate text if too long (keep first ~8000 chars for context)
        max_text_length = 8000
        truncated_text = text[:max_text_length]
        if len(text) > max_text_length:
            truncated_text += "\n\n[... text truncated ...]"

        prompt = f"""Extract key insights from this research paper.

Paper Title: {title}

Paper Text:
{truncated_text}

Please analyze this paper and extract the following information:

1. PROBLEM: What problem or research question does this paper address? (2-3 sentences)
2. METHOD: What approach or method does the paper use? (2-3 sentences)
3. KEY RESULTS: What are the main results or findings? (2-3 sentences)
4. CONTRIBUTIONS: What are the key contributions? (bullet points)
5. RELATED WORK: What related work is referenced? (list 3-5 key papers/areas)
6. FUTURE DIRECTIONS: What future research directions are mentioned? (bullet points)
7. CLASSIFICATION: Is this foundational (introduces new concepts/methods) or incremental (improves existing work)?

Format your response as JSON:
{{
  "problem": "...",
  "method": "...",
  "key_results": "...",
  "contributions": ["...", "..."],
  "related_work": ["...", "..."],
  "future_directions": ["...", "..."],
  "classification": "foundational" or "incremental"
}}"""

        return prompt

    def _parse_response(self, response: str) -> PaperInsights:
        """Parse Claude response into PaperInsights.

        Args:
            response: Claude's JSON response

        Returns:
            Parsed PaperInsights

        Raises:
            ValueError: If parsing fails
        """
        import json

        from models import PaperInsights

        try:
            # Extract JSON from response (may have markdown wrapper)
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response.strip()

            # Parse JSON
            data = json.loads(json_str)

            # Create PaperInsights
            insights = PaperInsights(
                problem=data["problem"],
                method=data["method"],
                key_results=data["key_results"],
                contributions=data["contributions"],
                related_work=data["related_work"],
                future_directions=data["future_directions"],
                classification=data["classification"],
            )

            return insights

        except Exception as e:
            raise ValueError(f"Failed to parse response: {e}")
