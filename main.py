"""Paper Reader CLI."""

from datetime import datetime
from typing import Literal
from typing import cast

import click
from insight_extractor import InsightExtractor
from interest_manager import InterestManager
from models import Paper
from models import ResearchInterests
from paper_discovery import PaperDiscoverer
from paper_ingestor import PaperIngestor
from paper_store import PaperStore

# Initialize managers
interest_manager = InterestManager()
paper_store = PaperStore()
discoverer = PaperDiscoverer()
ingestor = PaperIngestor()
extractor = InsightExtractor()


@click.group()
def cli():
    """Paper Reader - Research paper tracking and insight extraction."""
    pass


@cli.command()
def init():
    """Initialize paper_reader with research interests."""
    click.echo("🎓 Paper Reader - Initialize Research Interests\n")

    # Get areas
    click.echo("Research Areas (broad topics):")
    click.echo("  Examples: deep learning, signal processing, computer vision")
    areas_input = click.prompt("Enter areas (comma-separated)", default="")
    areas = [a.strip() for a in areas_input.split(",") if a.strip()]

    # Get topics
    click.echo("\nSpecific Topics (narrow interests):")
    click.echo("  Examples: attention mechanisms, MIMO, object detection")
    topics_input = click.prompt("Enter topics (comma-separated)", default="")
    topics = [t.strip() for t in topics_input.split(",") if t.strip()]

    # Get arXiv categories
    click.echo("\narXiv Categories (optional):")
    click.echo("  Examples: cs.LG, eess.SP, cs.CV")
    click.echo("  See: https://arxiv.org/category_taxonomy")
    categories_input = click.prompt("Enter categories (comma-separated)", default="")
    categories = [c.strip() for c in categories_input.split(",") if c.strip()]

    # Save interests
    interests = ResearchInterests(areas=areas, topics=topics, arxiv_categories=categories)
    interest_manager.save(interests)

    click.echo("\n✅ Interests saved!")
    click.echo(f"   Areas: {', '.join(areas)}")
    click.echo(f"   Topics: {', '.join(topics)}")
    if categories:
        click.echo(f"   Categories: {', '.join(categories)}")


@cli.command()
@click.option("--days", default=7, help="Days to look back")
@click.option("--max-results", default=20, help="Maximum papers to find")
def discover(days: int, max_results: int):
    """Discover papers from arXiv based on interests."""
    click.echo("🔍 Discovering papers from arXiv...\n")

    # Load interests
    interests = interest_manager.load()
    if not interests:
        click.echo("❌ No interests configured. Run 'paper-reader init' first.")
        return

    # Discover papers
    try:
        candidates = discoverer.discover(interests, days=days, max_results=max_results)

        if not candidates:
            click.echo("No papers found matching your interests.")
            return

        click.echo(f"Found {len(candidates)} papers:\n")

        for i, paper in enumerate(candidates, 1):
            click.echo(f"{i}. {paper.title}")
            click.echo(f"   Authors: {', '.join(paper.authors[:3])}")
            click.echo(f"   Published: {paper.published_date[:10]}")
            click.echo(f"   ID: {paper.id}")
            click.echo(f"   URL: {paper.url}")
            click.echo()

        click.echo("💡 Add papers with: paper-reader add <arxiv_id>")

    except Exception as e:
        click.echo(f"❌ Error discovering papers: {e}")


@cli.command()
@click.argument("arxiv_id")
def add(arxiv_id: str):
    """Add paper by arXiv ID and extract insights."""
    click.echo(f"📄 Adding paper: {arxiv_id}\n")

    try:
        # Get paper metadata
        click.echo("Fetching metadata...")
        candidate = discoverer.get_by_id(arxiv_id)
        if not candidate:
            click.echo(f"❌ Paper {arxiv_id} not found on arXiv")
            return

        # Download and extract text
        click.echo("Downloading PDF...")
        pdf_path, paper_text = ingestor.ingest_from_arxiv(candidate)
        click.echo(f"✓ PDF saved: {pdf_path}")

        # Extract insights
        click.echo("Extracting insights with AI...")
        insights = extractor.extract(paper_text, candidate.title)
        click.echo("✓ Insights extracted")

        # Create paper
        interests = interest_manager.load()
        paper = Paper(
            id=candidate.id,
            title=candidate.title,
            authors=candidate.authors,
            url=candidate.url,
            pdf_path=str(pdf_path),
            added_date=datetime.now().isoformat(),
            interests=interests.topics if interests else [],
            insights=insights,
            status="to-read",
            notes="",
        )

        # Save to store
        paper_store.add(paper)

        click.echo("\n✅ Paper added successfully!")
        click.echo(f"   Title: {paper.title}")
        click.echo(f"   Problem: {insights.problem[:100]}...")
        click.echo(f"   Classification: {insights.classification}")

    except Exception as e:
        click.echo(f"❌ Error adding paper: {e}")
        raise


@cli.command()
def list():
    """List all papers in collection."""
    click.echo("📚 Your Paper Collection\n")

    papers = paper_store.list_all()

    if not papers:
        click.echo("No papers in collection yet.")
        click.echo("💡 Discover papers with: paper-reader discover")
        return

    # Group by status
    by_status = {"to-read": [], "reading": [], "read": []}
    for paper in papers:
        by_status[paper.status].append(paper)

    for status, papers_list in by_status.items():
        if papers_list:
            click.echo(f"{status.upper()} ({len(papers_list)}):")
            for paper in papers_list:
                click.echo(f"  • {paper.title}")
                click.echo(f"    {paper.id} - {paper.insights.classification if paper.insights else 'N/A'}")
            click.echo()


@cli.command()
@click.argument("query")
def search(query: str):
    """Search papers by text."""
    click.echo(f"🔎 Searching for: {query}\n")

    results = paper_store.search(query)

    if not results:
        click.echo("No papers found matching query.")
        return

    click.echo(f"Found {len(results)} papers:\n")

    for paper in results:
        click.echo(f"• {paper.title}")
        click.echo(f"  {paper.id}")
        if paper.insights:
            click.echo(f"  Problem: {paper.insights.problem[:100]}...")
        click.echo()


@cli.command()
@click.argument("paper_id")
def show(paper_id: str):
    """Show detailed information about a paper."""
    paper = paper_store.get(paper_id)

    if not paper:
        click.echo(f"❌ Paper {paper_id} not found")
        return

    click.echo(f"\n📄 {paper.title}\n")
    click.echo(f"ID: {paper.id}")
    click.echo(f"Authors: {', '.join(paper.authors)}")
    click.echo(f"Status: {paper.status}")
    click.echo(f"Added: {paper.added_date[:10]}")
    click.echo(f"URL: {paper.url}")

    if paper.insights:
        click.echo("\n🧠 INSIGHTS:")
        click.echo(f"\nProblem:\n{paper.insights.problem}")
        click.echo(f"\nMethod:\n{paper.insights.method}")
        click.echo(f"\nKey Results:\n{paper.insights.key_results}")
        click.echo("\nContributions:")
        for contrib in paper.insights.contributions:
            click.echo(f"  • {contrib}")
        click.echo(f"\nClassification: {paper.insights.classification}")


@cli.command()
@click.argument("paper_id")
@click.argument("status", type=click.Choice(["to-read", "reading", "read"]))
def update_status(paper_id: str, status: str):
    """Update paper reading status."""
    paper = paper_store.get(paper_id)

    if not paper:
        click.echo(f"❌ Paper {paper_id} not found")
        return

    paper.status = cast(Literal["to-read", "reading", "read"], status)
    paper_store.update(paper)

    click.echo(f"✅ Updated {paper.title}")
    click.echo(f"   Status: {status}")


@cli.command()
@click.argument("paper_id")
def delete(paper_id: str):
    """Delete paper from collection."""
    paper = paper_store.get(paper_id)

    if not paper:
        click.echo(f"❌ Paper {paper_id} not found")
        return

    if click.confirm(f"Delete '{paper.title}'?"):
        paper_store.delete(paper_id)
        click.echo("✅ Paper deleted")


if __name__ == "__main__":
    cli()
