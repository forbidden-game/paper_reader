# AI Assistant Guidance for Paper Reader

This file provides guidance to AI assistants when working with the Paper Reader tool.

---

## Tool Purpose

**Paper Reader** is a PhD research paper tracker that helps researchers in deep learning, communication, and signal processing:

1. **Discover** relevant papers from arXiv based on research interests
2. **Extract insights** automatically using Claude (problem, method, results, contributions)
3. **Organize** papers with searchable JSON storage
4. **Track** reading progress and generate reading lists

**Primary User**: PhD student who needs to stay current with foundational and recent research

**Primary Pain Point**: Extracting insights from PDFs is time-consuming (this is THE priority)

---

## Architecture Overview

### Design Philosophy

This tool follows the **`scenarios/blog_writer/` exemplar**:
- Multi-stage pipeline with clear components
- ~800-1000 lines total code
- Modular "bricks and studs" architecture
- Simple JSON storage (no database)
- Claude Code SDK for AI tasks
- Resumable operations with state management

### Key Principle: Two-Phase Development

**Phase 1 (Current)**: Smart Discovery + Insight Extraction
- Discover papers from arXiv
- Ingest PDFs or arXiv URLs
- Extract structured insights with Claude
- Store and search papers

**Phase 2 (Future)**: Knowledge Graph
- Citation extraction
- Connection discovery
- Graph visualization
- NOT in current scope - build Phase 1 first!

### Module Structure (The "Bricks")

```
paper_reader/
├── interest_manager/      # Manage research interests
│   └── core.py           # Load/save interests, suggest arXiv categories
│
├── paper_discovery/       # Find papers on arXiv
│   └── core.py           # Query arXiv API, filter by interests
│
├── paper_ingestor/        # Load papers from PDF or URL
│   └── core.py           # Download PDFs, extract text
│
├── insight_extractor/     # Extract insights using Claude (PRIORITY)
│   └── core.py           # Analyze: problem/method/results/contributions
│
├── paper_store/           # Store and search papers
│   └── core.py           # JSON storage, simple search
│
├── main.py                # CLI orchestration (~300 lines)
├── state.py               # Session state management
└── models.py              # Data structures (optional)
```

### Key Interfaces (The "Studs")

These are the contracts between modules - keep them stable:

```python
@dataclass
class ResearchInterests:
    areas: list[str]          # e.g., ["deep learning", "signal processing"]
    topics: list[str]         # e.g., ["attention mechanisms", "MIMO"]
    arxiv_categories: list[str]  # e.g., ["cs.LG", "eess.SP"]

@dataclass
class PaperCandidate:
    id: str                   # e.g., "arxiv:2301.12345"
    title: str
    authors: list[str]
    abstract: str
    url: str
    published_date: str
    arxiv_categories: list[str]

@dataclass
class Paper:
    id: str
    title: str
    authors: list[str]
    url: str
    pdf_path: str | None
    added_date: str
    interests: list[str]
    insights: PaperInsights
    status: Literal["to-read", "reading", "read"]
    notes: str

@dataclass
class PaperInsights:
    problem: str              # What problem does this address?
    method: str               # What approach/method?
    key_results: str          # Main findings
    contributions: list[str]  # Key contributions
    related_work: list[str]   # Papers mentioned
    future_directions: list[str]  # Suggested future work
    classification: Literal["foundational", "incremental"]
```

---

## Data Storage Format

### Directory Structure

```
.data/papers/
├── interests.json              # User's research interests
├── collection/                 # User's paper collection
│   ├── arxiv_2301.12345.json  # One file per paper
│   └── local_paper_001.json
├── candidates/                 # Discovered papers (not yet added)
│   └── arxiv_2301.67890.json
└── pdfs/                      # Downloaded PDFs
    └── arxiv_2301.12345.pdf
```

### Example: collection/arxiv_2301.12345.json

```json
{
  "id": "arxiv:2301.12345",
  "title": "Hierarchical Attention for Long Signals",
  "authors": ["Smith, J.", "Doe, A."],
  "url": "https://arxiv.org/abs/2301.12345",
  "pdf_path": ".data/papers/pdfs/arxiv_2301.12345.pdf",
  "added_date": "2025-10-31T14:30:00",
  "interests": ["deep-learning", "signal-processing"],
  "insights": {
    "problem": "Limited context window in transformers for long signals",
    "method": "Hierarchical attention with local and global views",
    "key_results": "20% improvement on benchmark X, reduces memory by 40%",
    "contributions": [
      "Novel hierarchical attention mechanism",
      "State-of-art on long-form signal tasks"
    ],
    "related_work": ["Attention Is All You Need", "Longformer"],
    "future_directions": [
      "Apply to multimodal signals",
      "Extend to streaming scenarios"
    ],
    "classification": "incremental"
  },
  "status": "to-read",
  "notes": ""
}
```

---

## Key Design Decisions

### 1. arXiv API for Discovery

**Why arXiv?**
- Perfect coverage for user's fields (DL, signal processing, communication)
- Free API with reasonable rate limits
- Standard in academic research
- Well-documented Python package

**Categories for user's interests:**
- Deep Learning: `cs.LG`, `cs.AI`
- Signal Processing: `eess.SP`, `eess.SY`
- Communication: `cs.IT` (Information Theory)

### 2. Claude Code SDK for Insight Extraction

**Why Claude Code SDK?**
- Already integrated in Amplifier
- Follows blog_writer pattern (like style extraction)
- Handles long documents (100K+ tokens)
- Structured output with prompting

**Extraction approach:**
- Single-pass extraction (not multi-stage)
- Parse response to structured PaperInsights
- Handle errors with retries
- Show progress for long operations

### 3. Simple JSON Storage

**Why JSON, not database?**
- Ruthless simplicity principle
- Easy to inspect and backup
- grep-able for manual search
- No setup or dependencies
- Can migrate to database if needed later

**Storage pattern:**
- One file per paper in `collection/`
- Immutable after creation (insights don't change)
- Candidates separate from collection
- PDFs in dedicated directory

### 4. Phased Development

**Why not build knowledge graph now?**
- Start minimal, grow as needed
- Validate Phase 1 solves core problem
- Learn what connections matter most
- Avoid over-engineering
- User can use tool immediately

---

## CLI Commands

```bash
# Initialize research interests
make paper-init

# Discover papers from arXiv
make paper-discover --days 7

# Add paper to collection
make paper-add <arxiv-id>
make paper-add <path-to-pdf>

# Search collection
make paper-search "attention mechanisms"

# Generate reading list
make paper-reading-list --unread
make paper-reading-list --topic "deep-learning"
```

---

## Implementation Guidelines

### Module Size and Complexity

Following blog_writer exemplar:
- **Main orchestration**: ~300 lines (main.py)
- **Each module**: 80-150 lines
- **Total project**: ~800-1000 lines
- **Keep it simple**: If a module exceeds 200 lines, consider splitting

### Code Style

- Use Python type hints consistently
- Dataclasses for data models
- Clear function names (no abbreviations)
- Docstrings for public functions
- Handle errors with clear messages

### Testing Approach

- Unit tests for each module
- Integration test for full workflow
- Manual test scenarios in README
- Mock external APIs (arXiv, Claude)

### Error Handling

**User-facing errors should be helpful:**
```python
# Bad
raise Exception("Error")

# Good
raise ValueError(
    f"Could not extract text from PDF: {pdf_path}\n"
    f"The PDF might be encrypted or corrupted.\n"
    f"Try downloading it again from arXiv."
)
```

### Progress Reporting

For long operations, show progress:
```python
logger.info("Discovering papers from arXiv...")
logger.info(f"Found {len(candidates)} candidates")
logger.info(f"Extracting insights from {title}...")
logger.info(f"Saved to {output_path}")
```

---

## Dependencies

Add to `pyproject.toml`:

```toml
[project]
dependencies = [
    "arxiv",           # arXiv API access
    "pypdf",           # PDF text extraction
    "click",           # CLI framework
    "claude-code-sdk", # Already present
]
```

---

## Common Pitfalls to Avoid

### 1. Don't Over-Engineer

❌ **Bad**: Complex graph database, multiple storage backends, caching layers
✅ **Good**: Simple JSON files, direct arXiv API calls

### 2. Don't Build Phase 2 Features Yet

❌ **Bad**: Citation extraction, connection discovery, graph visualization
✅ **Good**: Focus on discovery and insight extraction only

### 3. Don't Ignore the Exemplar

❌ **Bad**: Create completely different structure
✅ **Good**: Follow blog_writer pattern closely

### 4. Don't Skip Progress Reporting

❌ **Bad**: Silent operation, user doesn't know what's happening
✅ **Good**: Show what's being processed, progress indicators

### 5. Don't Make Extraction Too Complex

❌ **Bad**: Multi-stage extraction with separate calls for each insight type
✅ **Good**: Single Claude call extracts all insights at once

---

## Workflow Example

### Typical User Flow

```bash
# 1. First-time setup
$ make paper-init
Enter research areas (comma-separated): deep learning, signal processing
Enter specific topics: attention mechanisms, MIMO, beamforming
✓ Interests saved to .data/papers/interests.json

# 2. Discover papers
$ make paper-discover --days 7
Searching arXiv for papers in: cs.LG, cs.AI, eess.SP, cs.IT
Found 23 papers
Filtering by interests...
Found 5 relevant papers
✓ Saved to .data/papers/candidates/

# 3. Add paper to collection
$ make paper-add arxiv:2301.12345
Fetching paper from arXiv...
Downloading PDF...
Extracting text...
Extracting insights with Claude...
✓ Paper added to collection

# 4. Search collection
$ make paper-search "attention"
Found 3 papers:

1. Hierarchical Attention for Long Signals (2023)
   Problem: Limited context window in transformers
   Status: to-read

2. Sparse Attention Mechanisms (2023)
   Problem: Quadratic complexity of attention
   Status: reading
```

---

## Integration with Amplifier

### Uses Existing Infrastructure

- **Claude Code SDK**: For insight extraction (like blog_writer uses for style)
- **State management**: Session state pattern from blog_writer
- **CLI patterns**: Click-based commands like other scenarios
- **Data storage**: `.data/` directory convention

### Fits in Project Structure

```
amplifier/
├── scenarios/
│   ├── blog_writer/        # Exemplar to follow
│   ├── article_illustrator/
│   └── ...
├── paper_reader/           # This tool (root level, not in scenarios/)
│   ├── interest_manager/
│   ├── paper_discovery/
│   └── ...
└── amplifier/              # Shared infrastructure
    └── ccsdk_toolkit/      # Could use defensive utilities
```

---

## Future Enhancements (Phase 2)

**NOT in current scope - document for reference:**

### Knowledge Graph Features
- Citation extraction from PDFs
- Relationship discovery (shared concepts, methods)
- Graph visualization
- Enhanced search using graph traversal
- Connection recommendations

### Implementation approach (when ready):
- Can leverage `amplifier/knowledge/` modules
- Graph stored as separate JSON structure
- Keep collection/ unchanged (backward compatible)
- Add new commands: `paper-graph`, `paper-connections`

---

## Testing Strategy

### Unit Tests

Create tests for each module:
```python
# test_insight_extractor.py
def test_extract_insights_from_sample_text():
    text = "Sample paper text..."
    insights = extract_insights(text, "Sample Paper")
    assert insights.problem != ""
    assert len(insights.contributions) > 0
    assert insights.classification in ["foundational", "incremental"]
```

### Integration Test

Test full workflow:
```python
# test_workflow.py
def test_add_paper_workflow(tmp_path):
    # Mock arXiv API and Claude
    paper_id = "arxiv:2301.12345"
    add_paper(paper_id, data_dir=tmp_path)

    # Verify paper in collection
    papers = list_papers(data_dir=tmp_path)
    assert len(papers) == 1
    assert papers[0].insights.problem != ""
```

### Manual Testing

Follow README examples with real papers to ensure:
- arXiv API works correctly
- PDF extraction handles various formats
- Claude extraction produces quality insights
- Search returns relevant results

---

## Questions to Ask When Implementing

Before starting any component:

1. **Does this follow blog_writer pattern?**
   - Similar module structure?
   - Similar size and complexity?
   - Using same patterns (state, CLI, Claude SDK)?

2. **Is this the simplest approach?**
   - Can I remove complexity?
   - Am I future-proofing unnecessarily?
   - Would JSON work instead of a database?

3. **Does this solve the user's priority?**
   - User's #1 need: Extract insights from PDFs
   - User's #2 need: Discover papers by interests
   - Everything else is secondary

4. **Can this be regenerated from the spec?**
   - Clear interfaces?
   - Self-contained modules?
   - Documented decisions?

---

## Success Metrics

### Phase 1 is successful when:

**Functional**:
- ✅ User can initialize interests
- ✅ User can discover papers from arXiv
- ✅ User can add papers (arXiv or PDF)
- ✅ User can extract insights automatically
- ✅ User can search and create reading lists

**Technical**:
- ✅ Follows blog_writer patterns
- ✅ ~800-1000 lines of code
- ✅ All tests pass
- ✅ No critical bugs

**User Experience**:
- ✅ Solves primary pain point (insight extraction)
- ✅ Commands are intuitive
- ✅ Errors are helpful
- ✅ Operations show progress

---

## Resources

### Related Documentation
- [DDD Plan](../ai_working/ddd/plan.md) - Complete implementation plan
- [blog_writer/](../scenarios/blog_writer/) - Exemplar to follow
- [IMPLEMENTATION_PHILOSOPHY.md](../ai_context/IMPLEMENTATION_PHILOSOPHY.md)
- [MODULAR_DESIGN_PHILOSOPHY.md](../ai_context/MODULAR_DESIGN_PHILOSOPHY.md)

### External Resources
- [arXiv API](https://arxiv.org/help/api) - Paper discovery
- [arxiv Python package](https://github.com/lukasschwab/arxiv.py) - API wrapper
- [pypdf](https://pypdf.readthedocs.io/) - PDF text extraction
- [Claude Code SDK](https://docs.anthropic.com/en/docs/claude-code) - AI integration

---

## Remember

**Core Principle**: This tool solves a PhD student's real pain point (extracting insights from papers) using Amplifier's patterns for reliability and maintainability.

**Start Simple**: Phase 1 only. Validate before building Phase 2.

**Follow the Exemplar**: blog_writer shows how to structure multi-stage AI tools in Amplifier.

**User First**: Every decision should make the tool easier for a PhD student to use.

---

**Built with Amplifier following ruthless simplicity and modular design.**
