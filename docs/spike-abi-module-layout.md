# ABI Module Layout Spike

> **Historical document.** This spike was run before implementation. Some findings
> diverged from the final code — see the notes at the bottom of each section.

## Context

Before building the ABI integration, we needed to understand the current module
structure, APIs, and registration mechanism.

## Goal

Understand what concrete files we need to create, what classes to subclass, and how to
wire the docsbot module into a running ABI instance.

## Questions

| # | Question |
|---|----------|
| Q1 | Where do custom modules live in the ABI repo? |
| Q2 | What class must a module subclass, and what's the required shape? |
| Q3 | How are modules registered / discovered? |
| Q4 | What's the API for loading triples into Oxigraph? |
| Q5 | What's the pattern for a Pipeline? |
| Q6 | What's the pattern for a Workflow (SPARQL tool)? |
| Q7 | What's the pattern for an Agent? |
| Q8 | How does the module get installed into ABI's Python environment? |

---

## Findings

### Q1 — Where do custom modules live?

Custom modules must be importable Python packages placed in the ABI repo root, then
registered in `config.yaml`. A cleaner long-term path is a pip-installable package.

### Q2 — Module class shape

Every module must:
- Subclass `BaseModule` from `naas_abi_core.module.Module`
- Declare an inner `Configuration` class subclassing `ModuleConfiguration`
- Implement `on_initialized()` (called after all modules and services are ready)

### Q3 — Module registration

```yaml
modules:
  - module: docsbot
    enabled: true
    config:
      graph_path: "../docs_bot/graph/docs_graph.ttl"
```

### Q4 — Triple store API

```python
triple_store.insert(graph: rdflib.Graph, graph_name: URIRef)
triple_store.query(sparql: str)   # returns iterable of rdflib ResultRows
```

> **Implementation note:** `insert()` requires a `graph_name` argument (named graph URI).
> Triples inserted without one go to the default graph and are invisible to queries that
> use `FROM <named-graph>`. All docsbot triples go into
> `<http://docsbot.local/graph/docs>`.

### Q5 — Pipeline pattern

```python
from naas_abi_core.pipeline import Pipeline, PipelineConfiguration, PipelineParameters

@dataclass
class MyPipelineConfiguration(PipelineConfiguration):
    triple_store: ITripleStoreService

class MyPipeline(Pipeline):
    def run(self, parameters: PipelineParameters) -> ...: ...
    def as_tools(self) -> list[BaseTool]: ...
    def as_api(self, router, ...): ...
```

### Q6 — Workflow pattern

Same structure as Pipeline but subclasses `Workflow`. `as_tools()` returns
`StructuredTool` instances.

### Q7 — Agent pattern

> **Implementation divergence:** The spike planned to use `IntentAgent`, but
> `IntentAgent.__init__` always instantiates `IntentMapper`, which calls
> `_resolve_default_embedding_model()`. This fails if no embedding model is registered.
> DocsBot only needs SPARQL tools, so it subclasses `Agent` (the base class) instead.

```python
from naas_abi_core.services.agent.Agent import Agent, AgentConfiguration, AgentSharedState

class DocsBotAgent(Agent):
    name: str = "DocsBot"

    @classmethod
    def New(cls, agent_shared_state=None, agent_configuration=None):
        ...
        return cls(name=cls.name, description=cls.description, chat_model=chat_model,
                   tools=tools, state=agent_shared_state, configuration=agent_configuration,
                   memory=None)
```

### Q8 — Installation into ABI's Python environment

```bash
make abi-install   # creates symlink: ../abi/docsbot → docs_bot/abi_module/docsbot
```

> **Implementation note:** The spike described setting `DOCS_GRAPH_PATH` as an env var.
> The final implementation uses `graph_path` in `config.yaml` (under the `docsbot`
> module config), not an env var.

---

## Answers summary

| Q | Answer |
|---|--------|
| Q1 | Custom modules go inside ABI repo as a Python package, registered by import path |
| Q2 | Subclass `BaseModule`; inner `Configuration(ModuleConfiguration)`; implement `on_initialized` |
| Q3 | Declare in `config.yaml` under `modules:` |
| Q4 | `triple_store.insert(rdflib.Graph, graph_name=URIRef(...))` + `triple_store.query(sparql)` |
| Q5 | Subclass `Pipeline`; implement `run()` and `as_tools()` |
| Q6 | Subclass `Workflow`; implement query method and `as_tools()` returning `StructuredTool` |
| Q7 | Subclass `Agent` (not `IntentAgent`) — IntentAgent requires embeddings |
| Q8 | Symlink via `make abi-install`; graph path set in `config.yaml`, not env var |
