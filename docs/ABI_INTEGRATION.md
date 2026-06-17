# ABI / Naas Integration

How to run DocsBot as a chat agent inside a
[Naas.ai](https://naas.ai) workspace via the
[jupyter-naas/abi](https://github.com/jupyter-naas/abi) framework.

This is the advanced path. For most uses, `python docsbot.py` (the standalone agent)
is simpler and has no ABI dependency. Use this path if you want DocsBot accessible
to collaborators through the Naas workspace UI without them running anything locally.

---

## Prerequisites

- A running ABI instance (`git clone https://github.com/jupyter-naas/abi.git ../abi`)
- Oxigraph running (`python -m naas_abi_core.services.triple_store.oxigraph_server`)
- `make graph` completed in this repo (produces `graph/docs_graph.ttl`)
- Both `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` in `../abi/.env`
  (ABI's ClaudeAgent requires OpenAI for embeddings even when using Claude for chat)

---

## Setup

### 1. Symlink the module

```bash
make abi-install              # defaults to ABI_DIR=../abi
# or: make abi-install ABI_DIR=/path/to/abi
```

This creates `../abi/docsbot → abi_module/docsbot` so `import docsbot` works inside
ABI's virtualenv. Changes to the module here are reflected immediately — no reinstall.

### 2. Register in config.yaml

Add to `../abi/config.yaml` under `modules:`:

```yaml
- module: docsbot
  enabled: true
  config:
    graph_path: "../docs_bot/graph/docs_graph.ttl"
```

Add the Anthropic module if not already present:

```yaml
- module: naas_abi_marketplace.ai.anthropic
  enabled: true
  config:
    anthropic_api_key: "{{ secret.ANTHROPIC_API_KEY }}"
- module: naas_abi_marketplace.ai.chatgpt
  enabled: true
  config:
    openai_api_key: "{{ secret.OPENAI_API_KEY }}"   # needed for embeddings
```

Under `services.model_registry`:
```yaml
services:
  model_registry:
    default_chat_model: "claude-sonnet-4-5"
    default_embedding_model: "text-embedding-3-large"
```

Under the `naas_abi` module config (sibling of `nexus_config`, not inside it):
```yaml
- module: naas_abi
  enabled: true
  config:
    abi_agent_model: "claude-sonnet-4-5"
    ontology_engineer_model: "claude-sonnet-4-5"
    nexus_config:
      ...
```

### 3. Load the graph

With ABI and Oxigraph running:

```bash
make abi-load
```

This runs `LoadGraphPipeline`, which parses `graph/docs_graph.ttl` and inserts all
triples into Oxigraph. The pipeline is idempotent — safe to re-run after `make graph`.

### 4. Start ABI

```bash
cd ../abi && make api
```

DocsBot appears at `http://localhost:9879/agents/DocsBot/completion`. Test with:

```bash
curl -X POST http://localhost:9879/agents/DocsBot/completion \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"messages": [{"role": "user", "content": "Which tasks mention actor?"}]}'
```

---

## Module layout

```
abi_module/docsbot/
  __init__.py                ABIModule — registers with ABI engine, declares TripleStoreService dep
  ontologies/
    docs_ontology.ttl        OWL schema — auto-loaded by ABI at startup
  pipelines/
    LoadGraphPipeline.py     Parses docs_graph.ttl, bulk-inserts into Oxigraph
  workflows/
    FindTasksWorkflow.py     Tasks mentioning a term
    ImpactAnalysisWorkflow.py  Blast-radius count + topic list for a term
    TopicsBySubjectWorkflow.py  Topics tagged with a taxonomy subject
    OrphanTopicsWorkflow.py   Topics with no inbound references
  agents/
    DocsBotAgent.py          Agent — wires the four workflows as tools, uses Agent base class
```

Each workflow is the same SPARQL query as `agent/sparql.py`, wrapped in ABI's
`Workflow` / `WorkflowConfiguration` / `WorkflowParameters` / `StructuredTool` pattern.
Read both side-by-side to see exactly what the framework adds.

---

## Key implementation notes

- `DocsBotAgent` subclasses `Agent` (not `IntentAgent`). `IntentAgent` requires an
  embedding model for intent mapping; DocsBot only needs SPARQL tools, so the simpler
  base class is correct.
- All SPARQL queries include `FROM <http://docsbot.local/graph/docs>`. Oxigraph is a
  quad store; triples inserted with a named graph are invisible to queries that don't
  specify that graph.
- The `TripleStoreService` (concrete class) must be listed in `dependencies`, not
  `ITripleStoreService` (interface) — ABI's engine checks for the concrete class.
