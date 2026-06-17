# What This System Is, and Why It Matters

*A plain-language guide for technical writers who live in Confluence and want AI that
actually knows their docs.*

## The problem this solves

If you've tried pointing an AI chatbot at your documentation, you've probably seen the
failure mode: it answers confidently, cites nothing, and is wrong just often enough that
you can't trust it. That happens because most "chat with your docs" tools work by chopping
your pages into arbitrary chunks of text, converting them to numbers, and fuzzy-matching
against questions. The AI never knows that *Deploy a Ray Serve Application* is a procedure,
that it depends on the *Deployment* concept, or that changing one page quietly breaks claims
made on dozens of others. It just sees soup.

This system takes the opposite approach, borrowed from Michael Iantosca's work in
enterprise content engineering: **make the structure explicit, and let the AI navigate
facts instead of guessing from text.**

## How it works, in five moves

**1. Content lives as files, not just pages.** Every topic is a plain text file in a
folder — the "docs-as-code" part. Files can be versioned, diffed, reviewed, and processed
by scripts. Confluence becomes a *publishing target*, not the only home of the content.

**2. Every topic declares what it is.** A small header on each file records its type —
*concept* (what something is), *task* (how to do something), *reference* (lookup material),
or *glossary term* (definition of one word). Writers who know DITA will recognize this as
information typing. It's the single highest-leverage piece of metadata in the system.

**3. A shared vocabulary ties everything together.** The glossary isn't an afterthought;
it's the spine. Every time a topic mentions a defined term, that becomes a recorded link:
*this task mentions "Actor."* Those links are found by scanning the text against a known
glossary — no AI interpretation required. The connections come from structure, not inference.

**4. The structure becomes a knowledge graph.** All of those facts — types, terms,
mentions, cross-references, which section contains what — get compiled into a graph
database. Think of it as a map of your documentation where every relationship is a road:
this page *defines* that term, *mentions* these others, *belongs to* this section.

**5. The AI answers by reading the map.** When someone asks "which procedures involve
Actors?", the AI doesn't skim text and hope. It runs a precise query against the graph
and gets the exact set of pages, with their locations. The language model's job shrinks
to what it's good at — understanding the question and phrasing the answer — while the
*facts* come from a database that is either right or empty, never creative.

Meanwhile, the same pipeline publishes everything to Confluence as a normal page tree,
with the metadata visible on each page. Your readers see Confluence. The AI sees the graph.
Both are generated from the same files, so they can't drift apart.

## What makes this powerful

**Deterministic answers.** "Which topics mention this term?" has one correct answer, and
the graph returns it. This is the difference between an AI that *retrieves* and one that
*recalls vaguely*. For documentation — where being almost right is being wrong — this is
the property that matters most.

**Impact analysis becomes a query.** Before this, "what breaks if we rename this feature?"
meant search-and-pray. Now it's one query: 129 topics mention *Actor*; here they are,
grouped by type. That's a content strategy tool, not just an AI feature.

**Writers' existing discipline is the fuel.** Nothing here requires new skills beyond what
good structured authoring already asks: type your topics, maintain a glossary, link
deliberately. The system converts editorial discipline directly into AI reliability. Teams
with strong information architecture get a strong graph for free; the graph also makes
weak spots visible (orphan pages, untyped content, undefined terms).

**Everything is inspectable.** When the AI cites a relationship, you can open the graph
file and find the exact triple that asserts it. Compare that to a vector database, which
cannot explain itself even in principle.

**It's all free and portable.** Open formats (Markdown, Turtle/RDF, SPARQL), open-source
tools, Confluence's free plan, and a locally-run agent. Nothing is locked in; Confluence
could be swapped for another output tomorrow without touching the pipeline.

## Honest weaknesses

**The graph only knows what's marked up.** If a topic mentions "actor" in the prose but
the term isn't in the glossary, the connection is invisible. The system's precision is
bounded by vocabulary coverage.

**It inherits your metadata debt.** Plugging in a legacy wiki full of untyped,
unstructured pages gives you a sparse, low-value graph. This demo uses Ray documentation,
which was already well-structured; most real Confluence spaces are not. Budget real
editorial work for retrofitting, or accept that the graph grows page by page.

**One-way publishing.** Files flow *to* Confluence. If colleagues edit pages directly in
Confluence, those edits are stranded — the next publish overwrites them. This is the
deepest cultural change for Confluence-native teams: the file repository, not the wiki,
becomes the source of truth.

**The graph answers "what," not "why."** It knows *task X mentions term Y*; it does not
know whether the procedure's steps are correct or the explanation is clear. Questions
needing actual comprehension of prose still fall to the language model reading text, with
the usual caveats. The strongest setups are hybrid — graph for facts and navigation, text
retrieval for substance — and this system covers the first half excellently.

**Moving parts.** Scraper, enricher, graph builder, publisher, agent. It's all small,
readable Python, but it's a pipeline someone has to own. Not a SaaS product with a support
team.

**Scale is unproven here.** ~500 topics build in seconds. Tens of thousands of topics
across multiple products and versions will need real engineering — incremental builds,
versioned graphs, deliberate ontology governance.

## The takeaway

The pitch to a docs team is one sentence: **your structure becomes the AI's brain.**
Everything you already believe in — topic typing, controlled vocabulary, deliberate
linking — stops being invisible hygiene and becomes the literal substrate that makes an
AI trustworthy. The cost is discipline and a source-of-truth shift; the payoff is an
assistant that cites real pages, knows your terminology, and can tell you the blast
radius of any change before you make it.
