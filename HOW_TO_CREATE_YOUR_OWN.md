# How to Create Your Own Amplifier Tool

**Learning from Paper Reader: The design process behind this tool**

## What This Document Is

This isn't a coding tutorial. It's a design guide.

You'll learn:
- **The thinking process** that created Paper Reader
- **The metacognitive recipe** (how to break down problems)
- **How to work with Amplifier** to build similar tools
- **Design decisions and trade-offs** we made

**The goal**: Enable you to create your own Amplifier-powered tools by describing what you want.

## The Starting Point

### The User's Need

A PhD student said:
> "I need a tool to keep up with foundational and recent research in deep learning, communication, and signal processing. I want to discover papers based on my interests and extract insights automatically. Building a knowledge graph would be nice eventually, but first I need the basics working."

That's it. No technical spec. No architecture diagram. Just a clear need.

### The Key Questions

Before touching code, we asked:

1. **What's the primary pain point?**
   - Extracting insights from papers takes too long

2. **What does discovery mean?**
   - User enters interests → tool finds relevant papers

3. **What insights matter?**
   - Problem, method, results, contributions, related work

4. **What comes later?**
   - Knowledge graph showing connections between papers

These questions shaped everything.

## The Metacognitive Recipe

A **metacognitive recipe** is the thinking process - "How should AI approach this problem?"

Here's Paper Reader's recipe:

### Stage 1: Manage Interests
"The user needs to tell the system what they care about."

**Thinking**:
- Research areas (broad): "deep learning", "signal processing"
- Specific topics (narrow): "attention mechanisms", "MIMO"
- System maps these to arXiv categories: cs.LG, eess.SP, etc.

**Output**: interests.json file

### Stage 2: Discover Papers
"Given interests, find relevant recent papers from arXiv."

**Thinking**:
- Query arXiv API for papers in relevant categories
- Filter by user's topics in title/abstract
- Present candidates for review before adding

**Output**: List of paper candidates with metadata

### Stage 3: Ingest Papers
"Get the paper content, whether from arXiv or local PDF."

**Thinking**:
- If arXiv ID: download PDF automatically
- If local PDF: use provided file
- Extract text from PDF

**Output**: Plain text of paper

### Stage 4: Extract Insights
"Analyze the paper to extract structured insights."

**Thinking**:
- Single Claude call extracts everything at once
- Parse response into structured format
- Handle errors gracefully

**Output**: PaperInsights object with problem/method/results/etc.

### Stage 5: Store and Search
"Save papers with insights, make them searchable."

**Thinking**:
- One JSON file per paper
- Simple text search across fields
- Track reading status

**Output**: Searchable collection in .data/papers/

## Why This Recipe Works

### 1. Clear Stages
Each stage has one responsibility:
- Interests: Capture what user cares about
- Discovery: Find relevant papers
- Ingestion: Get paper content
- Extraction: Pull out key insights
- Storage: Organize and search

### 2. Right-Sized Tasks
No stage is overwhelming:
- Each does 1 thing well
- Each can be built/tested independently
- Each has clear inputs and outputs

### 3. Progressive Value
User gets value at each stage:
- Stage 1: Interests saved (they can review)
- Stage 2: Papers discovered (they can browse)
- Stage 3: PDFs downloaded (they have content)
- Stage 4: Insights extracted (main value delivered)
- Stage 5: Collection organized (they can search)

### 4. Extensible
Easy to add more later:
- Citation extraction (new stage)
- Connection discovery (new stage)
- Graph visualization (new stage)

## Design Decisions

### Decision 1: arXiv Only (For Now)

**Choice**: Use arXiv API exclusively

**Why**:
- Covers user's fields completely (CS, EE fields)
- Free, reliable API
- Standard in academic research
- Can add other sources later (Google Scholar, Semantic Scholar)

**Trade-off**: Misses papers not on arXiv (but most ML/SP papers are there)

### Decision 2: Simple JSON Storage

**Choice**: One JSON file per paper

**Why**:
- Ruthless simplicity principle
- Easy to inspect and backup
- No database setup required
- grep-able for manual search

**Trade-off**: Slower search at scale (but fine for hundreds of papers)

### Decision 3: Single-Pass Extraction

**Choice**: Extract all insights in one Claude call

**Why**:
- Faster (1 API call vs. 6+)
- Consistent context across all extractions
- Simpler code (no orchestration needed)

**Trade-off**: Slightly less specialized than multi-stage extraction

### Decision 4: Phase 1 Before Phase 2

**Choice**: Build discovery + extraction first, knowledge graph later

**Why**:
- Validate core value before adding complexity
- Learn what connections matter most
- Start minimal, grow as needed

**Trade-off**: User doesn't get graph features immediately

### Decision 5: Status Tracking Not Priority

**Choice**: Simple status field (to-read/reading/read), not detailed tracking

**Why**:
- User's priority was insight extraction, not tracking
- Can add detailed progress tracking later if needed
- Keep MVP focused

**Trade-off**: Less granular than some research tools

## How to Create Your Own Tool

### Step 1: Define the Problem Clearly

**Bad**: "I want something that helps with research"

**Good**: "I need to extract insights from research papers and discover relevant papers based on my interests"

**Key**: Be specific about:
- **Pain point**: What's frustrating?
- **Outcome**: What does success look like?
- **Priority**: What matters most?

### Step 2: Break Into Stages

Ask: "What are the logical steps?"

**For Paper Reader**:
1. What interests you? → Manage interests
2. Find relevant papers → Discovery
3. Get paper content → Ingestion
4. What's important? → Extraction
5. Organize and find → Storage/Search

**Your tool**: What are its natural stages?

### Step 3: Define Stage Inputs/Outputs

For each stage:

**Inputs**: What does this stage need?
**Outputs**: What does this stage produce?
**Success**: How do you know it worked?

**Example**:
- **Stage**: Insight Extraction
- **Input**: Paper text, title
- **Output**: PaperInsights (problem, method, results, etc.)
- **Success**: Insights are accurate and structured

### Step 4: Start With Simplest Version

**Don't build**:
- Multiple paper sources
- Advanced search
- Knowledge graphs
- Complex tracking

**Do build**:
- One paper source (arXiv)
- Basic search (text matching)
- Core extraction (insights only)
- Simple storage (JSON files)

**Add later**: Everything else

### Step 5: Describe to Amplifier

Use the `/ddd:1-plan` command and describe:

**Your problem**:
"I'm a [role] who needs to [goal] because [pain point]"

**Your stages**:
"The tool should think through this by:
1. First, [stage 1]
2. Then, [stage 2]
3. Then, [stage 3]"

**Your priorities**:
"Most important: [priority 1]
Nice to have: [priority 2]
Future: [priority 3]"

That's it. Amplifier handles implementation.

## Common Patterns

### Pattern 1: Discovery → Process → Store

**Applies when**: You need to find things, process them, and organize results

**Examples**:
- Paper Reader: Discover papers → Extract insights → Store
- Blog Writer: Find style → Generate content → Review/refine
- Image Analyzer: Find images → Analyze content → Categorize

**Recipe**:
1. Discovery stage (what to process?)
2. Processing stage (extract value)
3. Storage stage (organize results)

### Pattern 2: User Input → AI Analysis → Structured Output

**Applies when**: You need AI to extract structure from unstructured content

**Examples**:
- Paper Reader: PDF → Insights extraction → Structured JSON
- Meeting Notes: Audio → Transcribe → Action items
- Code Review: Code → Analysis → Issues + suggestions

**Recipe**:
1. Ingest unstructured input
2. Single Claude call with structured prompt
3. Parse to defined format

### Pattern 3: Progressive Refinement

**Applies when**: Initial output needs iteration based on user feedback

**Examples**:
- Blog Writer: Draft → Review → Incorporate feedback → Final
- Paper Reader (future): Graph → Review → Adjust connections → Final

**Recipe**:
1. Generate initial version
2. Present to user for feedback
3. Refine based on feedback
4. Repeat until approved

## Architecture Principles

### Principle 1: Bricks and Studs

**Bricks**: Self-contained modules
- Each has clear responsibility
- Can be regenerated independently
- Internal implementation can change

**Studs**: Connection points (interfaces)
- Data models (ResearchInterests, Paper, etc.)
- Function signatures
- CLI commands

**Keep studs stable**, bricks flexible.

### Principle 2: Code for Structure, AI for Intelligence

**Code handles**:
- Pipeline orchestration
- State management
- File I/O
- Error handling
- Progress reporting

**AI handles**:
- Understanding content
- Extracting insights
- Making judgments
- Creative reasoning

Don't use AI for what code does better. Don't use code for what AI does better.

### Principle 3: Ruthless Simplicity

**Always ask**:
- Do we need this now?
- What's the simplest approach?
- Can we do this more directly?

**Examples**:
- JSON > Database (for now)
- arXiv only > Multiple sources
- Text search > Vector embeddings
- Single Claude call > Multi-stage pipeline

**Add complexity only when proven necessary.**

### Principle 4: Progressive Value

User should get value at each stage:
- Stage 1 completes → Something works
- Stage 2 completes → More value added
- Stage 3 completes → Even more value

**Not**: All or nothing

**Instead**: Incremental wins

## Practical Tips

### Tip 1: Document the Recipe First

Before any code, write:
```markdown
# Tool Recipe

## Stage 1: [Name]
Thinking: [What this stage does and why]
Input: [What it needs]
Output: [What it produces]

## Stage 2: [Name]
...
```

Share with Amplifier using `/ddd:1-plan`.

### Tip 2: Use blog_writer as Exemplar

Paper Reader follows blog_writer structure:
- Multi-stage pipeline
- State management for resumability
- Click-based CLI
- Simple JSON storage
- ~800-1000 lines total

Study blog_writer first. Copy its patterns.

### Tip 3: Test Each Stage Independently

**Don't** build all stages then test.

**Do** test each stage as you build:
- Stage 1 works → Test it
- Stage 2 works → Test it
- Full pipeline → Test it

### Tip 4: Start Minimal, Measure, Grow

**Build**:
- Simplest version that solves core problem

**Use it**:
- For at least 1-2 weeks

**Learn**:
- What's missing?
- What's annoying?
- What would help most?

**Add**:
- Only what you actually need

### Tip 5: Embrace Regeneration

Your tool is built from specs, not hand-crafted.

**Want to change something?**
1. Update the spec
2. Regenerate the module
3. Test it

**Don't**: Edit code line-by-line

**Do**: Regenerate from improved spec

## What Makes a Good Amplifier Tool?

### 1. Solves Real Problem
Not "what if..." but "I need to..."

### 2. Clear Thinking Process
You can describe stages in plain English.

### 3. Right-Sized Stages
Each stage is understandable and testable.

### 4. Progressive Value
User gets wins early and often.

### 5. Simple First, Complex Later
MVP proves value before adding features.

## Your Turn

### Exercise: Design Your Tool

**Step 1**: Describe your need
```
I'm a [role] who needs to [goal] because [pain point]
```

**Step 2**: Break into stages
```
1. First, the tool should [stage 1]
2. Then, it should [stage 2]
3. Finally, it should [stage 3]
```

**Step 3**: Define success
```
I'll know it works when [measurable outcome]
```

**Step 4**: Share with Amplifier
```bash
/ddd:1-plan [your description]
```

That's it. Amplifier handles the rest.

## Real Example: This Tool Was Created Like This

### The Conversation

**User**: "I'm a PhD student in deep learning and signal processing. I need a tool to:
1. Discover papers based on my interests from arXiv
2. Extract insights automatically (problem, method, results)
3. Track what I've read
4. (Eventually) build a knowledge graph"

**Assistant**: "Let me use /ddd:1-plan to design this..."

[Planning conversation happens - asking clarifying questions]

**User**: "Yes, that design looks right!"

**Result**: Complete implementation plan in `ai_working/ddd/plan.md`

### What Came Next

1. **Phase 2 (Documentation)**: Write README, HOW_TO, AGENTS.md
2. **Phase 3 (Code Planning)**: Break implementation into chunks
3. **Phase 4 (Implementation)**: Build each chunk, test, iterate
4. **Phase 5 (Testing)**: Verify everything works

**Total**: ~2 weeks from idea to working tool.

**Key**: Clear problem definition + structured thinking → working tool.

## Resources

### Study These Examples

**blog_writer** (`scenarios/blog_writer/`)
- Multi-stage content generation
- Style extraction + generation + review
- State management patterns

**article_illustrator** (`scenarios/article_illustrator/`)
- Content analysis + image generation
- Multi-API integration
- Resumability patterns

**Paper Reader** (this tool)
- Discovery + extraction + storage
- arXiv integration
- Insight extraction patterns

### Read These Docs

**[IMPLEMENTATION_PHILOSOPHY.md](../ai_context/IMPLEMENTATION_PHILOSOPHY.md)**
- Ruthless simplicity principle
- When to use libraries vs. custom code
- Decision-making framework

**[MODULAR_DESIGN_PHILOSOPHY.md](../ai_context/MODULAR_DESIGN_PHILOSOPHY.md)**
- Bricks and studs concept
- Regeneratable modules
- Clear interfaces

**[Document-Driven Development](../docs/document_driven_development/)**
- Complete DDD process
- How to plan, document, implement
- Quality assurance patterns

## Remember

**You're not coding**. You're **designing**.

Describe what you want clearly.
Break it into logical stages.
Identify priorities.
Share with Amplifier.

**The code emerges from good design, not the other way around.**

---

**Built with Amplifier** - This tool and this guide both emerged from describing goals and thinking processes. You can create your own tools the same way.
