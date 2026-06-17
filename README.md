# docs_bot — Docs-as-Code + Knowledge Graph

A proof-of-concept pipeline that turns documentation into a structured knowledge graph
and exposes it through a Claude-powered chat agent. Modeled on Michael Iantosca's
graph-driven documentation framework.

The corpus is Ray documentation (Apache 2.0), scraped from
[ray-project/ray](https://github.com/ray-project/ray).

---

## What it does

Instead of fuzzy text search, **DocsBot** runs precise SPARQL queries against a knowledge
graph and returns deterministic answers:

- *"Which tasks mention the term actor?"* → exact list, with canonical paths
- *"What's the blast radius if we change the 'deployment' term?"* → 129 topics, by type
- *"Show me all Ray Serve topics"* → full inventory
- *"Which concept pages have no inbound links?"* → orphan list

The pipeline follows Iantosca's five steps:

| Step | Description | This repo |
|------|-------------|-----------|
| 1 | Componentized content | `content/raw/` — Ray docs, each topic a discrete file |
| 2 | Apply taxonomy | `scripts/enrich_metadata.py` → `content/enriched/` |
| 3 | Ontology | `ontology/docs_ontology.ttl` — OWL, BFO/CCO-aligned |
| 4 | RDF graph | `scripts/build_graph.py` → `graph/docs_graph.ttl` |
| 5 | Graph DB + agent | `docsbot.py` — Claude tool-use agent over Oxigraph |

---

## Quick start

```bash
git clone https://github.com/YOUR_USER/docs_bot.git
cd docs_bot
pip install -r requirements.txt
cp .env.example .env        # add ANTHROPIC_API_KEY
make scrape                 # pulls ~274 Ray docs into content/raw/
make enrich                 # classifies topics, extracts mentions/references
make graph                  # compiles to graph/docs_graph.ttl (~6,500 triples)
python docsbot.py           # interactive REPL
```

Single question:
```bash
python docsbot.py "What is the blast radius of changing the term actor?"
# or:
make chat Q="Which task topics mention placement groups?"
```

DocsBot loads the graph into memory (~1s), calls SPARQL tools via Claude's tool-use API,
and returns answers grounded in real graph data.

---

## Confluence publishing

Publishes the enriched docs as a browsable page tree.

```bash
# Add to .env:
#   CONFLUENCE_BASE_URL=https://your-site.atlassian.net
#   CONFLUENCE_EMAIL=you@example.com
#   CONFLUENCE_API_TOKEN=...       # https://id.atlassian.com/manage-profile/security/api-tokens
#   CONFLUENCE_SPACE_KEY=DOCS

make dry-run    # preview the page tree
make publish    # push ~274 pages to Confluence
```

Each page includes a metadata panel (topic type, subjects, mentioned terms) and a
CC/Apache attribution footer.

---

## Switching corpora

The pipeline is content-agnostic. To use different docs:

1. Add a scraper to `scripts/` (see `scrape_ray_docs.sh` as a template)
2. Update `taxonomy/taxonomy.yaml` with new subject areas
3. Update `taxonomy/glossary.yaml` with domain-specific terms
4. `make enrich graph` — everything downstream rebuilds automatically

The original Kubernetes scraper is preserved as `make scrape-k8s`.

---

## Repository layout

```
content/raw/          Scraped Ray docs (.md and .rst)
content/enriched/     Enriched docs with topic type, subjects, mentions (always .md)
taxonomy/             taxonomy.yaml — subject scheme; glossary.yaml — term definitions
ontology/             docs_ontology.ttl — OWL/Turtle schema
graph/                docs_graph.ttl — generated RDF; queries.rq — sample SPARQL
scripts/              scrape_ray_docs.sh, enrich_metadata.py, build_graph.py,
                      publish_confluence.py, query.py, scrape_k8s_docs.sh
agent/                sparql.py — four SPARQL query functions (no framework deps)
docsbot.py            Claude tool-use agent entry point
abi_module/docsbot/   Optional ABI/Naas integration (see docs/ABI_INTEGRATION.md)
docs/                 Additional documentation
```

---

## Learning guide

Read files in this order to follow the architecture:

1. `ontology/docs_ontology.ttl` — the RDF schema (classes, properties)
2. `taxonomy/taxonomy.yaml` + `taxonomy/glossary.yaml` — controlled vocabulary
3. `scripts/enrich_metadata.py` — how raw docs become typed, annotated metadata
4. `scripts/build_graph.py` — how metadata becomes RDF triples
5. `graph/queries.rq` — what the graph can answer (raw SPARQL)
6. `agent/sparql.py` — the four query functions, no framework dependency
7. `docsbot.py` — Claude tool-use loop wiring everything together
8. `abi_module/docsbot/workflows/FindTasksWorkflow.py` — same queries in ABI's framework
9. `docs/OVERVIEW_FOR_WRITERS.md` — plain-language explanation for non-engineers

---

## ABI / Naas integration (advanced)

`abi_module/docsbot/` contains the same four queries wrapped in Naas's ABI framework
(Workflow + Pipeline + Agent classes), exposing DocsBot as a chat agent in a Naas
workspace. This requires cloning [jupyter-naas/abi](https://github.com/jupyter-naas/abi)
separately. See `docs/ABI_INTEGRATION.md` for setup.

The standalone `docsbot.py` covers the same capability with far fewer dependencies —
use that unless you specifically need the Naas workspace UI.

---

## Licensing

Ray docs content: Apache 2.0, © The Ray Authors. Attribution preserved in page footers.
This repo's own code: MIT.
