"""
LoadGraphPipeline — bulk-load docs_graph.ttl into ABI's Oxigraph triple store.

When to run
-----------
Run this once after every `make graph` in the docs_bot repo (i.e. whenever the
RDF graph is rebuilt from updated content).  The Makefile target `make abi-load`
in docs_bot calls this pipeline via its __main__ block.

Why a Pipeline and not a plain script
--------------------------------------
ABI's Pipeline base class gives us:
- A standard Configuration / Parameters contract other code can depend on.
- as_tools() so the pipeline can optionally be exposed to agents as a tool
  (e.g. let the DocsBot agent reload the graph on demand).
- as_api() to expose it as a REST endpoint in the ABI API server.

How it works
------------
1. Parse docs_graph.ttl into an rdflib Graph (in-memory).
2. Pass the rdflib Graph to triple_store.insert(), which sends all triples
   to Oxigraph over HTTP.
3. Oxigraph persists them; subsequent SPARQL queries from the workflows hit
   the live store.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from langchain_core.tools import BaseTool, StructuredTool
from naas_abi_core import logger
from naas_abi_core.pipeline import Pipeline, PipelineConfiguration, PipelineParameters
from naas_abi_core.services.triple_store.TripleStorePorts import ITripleStoreService
from naas_abi_core.utils.Expose import APIRouter
from rdflib import Graph, URIRef

# Named graph URI that will hold all docsbot triples in Oxigraph.
# Using a dedicated URI keeps our triples separate from other modules' data
# and makes it easy to drop and reload the graph cleanly.
DOCSBOT_GRAPH = URIRef("http://docsbot.local/graph/docs")


# ---------------------------------------------------------------------------
# Configuration — holds dependencies injected at construction time
# ---------------------------------------------------------------------------

@dataclass
class LoadGraphPipelineConfiguration(PipelineConfiguration):
    """Injected once when the pipeline is constructed.

    Attributes:
        triple_store: The ABI triple store service (wraps Oxigraph HTTP API).
        graph_path:   Filesystem path to docs_graph.ttl.
    """
    triple_store: ITripleStoreService
    graph_path: str = "graph/docs_graph.ttl"


# ---------------------------------------------------------------------------
# Parameters — provided at each run() call
# ---------------------------------------------------------------------------

class LoadGraphPipelineParameters(PipelineParameters):
    """Per-run parameters.

    We don't need anything beyond what's in the configuration for a basic
    load, but keeping an explicit Parameters class lets callers pass a custom
    path at runtime (e.g. from an API request).

    Attributes:
        graph_path: Override the default path from configuration if provided.
    """
    graph_path: str = ""  # empty → use configuration default


# ---------------------------------------------------------------------------
# Pipeline implementation
# ---------------------------------------------------------------------------

class LoadGraphPipeline(Pipeline):
    """Parses the docs RDF graph and inserts all triples into Oxigraph."""

    __configuration: LoadGraphPipelineConfiguration

    def __init__(self, configuration: LoadGraphPipelineConfiguration) -> None:
        super().__init__(configuration)
        self.__configuration = configuration

    def run(self, parameters: PipelineParameters) -> int:
        """Load the graph file into the triple store.

        Args:
            parameters: LoadGraphPipelineParameters (path override optional).

        Returns:
            Number of triples inserted.
        """
        assert isinstance(parameters, LoadGraphPipelineParameters)

        # Resolve the path: parameter overrides configuration default.
        path_str = parameters.graph_path or self.__configuration.graph_path
        graph_path = Path(path_str).expanduser().resolve()

        if not graph_path.exists():
            logger.error(
                f"[docsbot] Graph file not found: {graph_path}. "
                "Run `make graph` in the docs_bot repo first."
            )
            return 0

        logger.info(f"[docsbot] Parsing RDF graph from {graph_path} ...")

        # rdflib parses Turtle (.ttl) files into an in-memory graph object.
        # Every subject–predicate–object triple in the file becomes one entry.
        g = Graph()
        g.parse(graph_path, format="turtle")
        triple_count = len(g)
        logger.info(f"[docsbot] Parsed {triple_count} triples.")

        # triple_store.insert() sends the entire rdflib Graph to Oxigraph.
        # Oxigraph merges them into its persistent store (no duplicates thanks
        # to the RDF set semantics — re-running this after a rebuild is safe).
        logger.info("[docsbot] Inserting triples into Oxigraph ...")
        self.__configuration.triple_store.insert(g, graph_name=DOCSBOT_GRAPH)
        logger.info(f"[docsbot] ✅ {triple_count} triples loaded into triple store.")

        return triple_count

    def as_tools(self) -> list[BaseTool]:
        """Expose as a LangChain tool so agents can trigger a graph reload."""
        return [
            StructuredTool(
                name="reload_docs_graph",
                description=(
                    "Reload the documentation knowledge graph from the TTL file into "
                    "the triple store.  Use this after the docs pipeline has been re-run "
                    "to pick up updated content."
                ),
                func=lambda **kwargs: self.run(LoadGraphPipelineParameters(**kwargs)),
                args_schema=LoadGraphPipelineParameters,
            )
        ]

    def as_api(
        self,
        router: APIRouter,
        route_name: str = "",
        name: str = "",
        description: str = "",
        description_stream: str = "",
        tags: list[str | Enum] | None = None,
    ) -> None:
        # Not exposing as a REST endpoint for this POC.
        return None


# ---------------------------------------------------------------------------
# CLI entry point — used by `make abi-load`
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    """Run as a standalone script to load the graph into a running ABI instance.

    Usage (from the ABI repo root, with docs_bot venv active):
        python -m docsbot.pipelines.LoadGraphPipeline

    Or via the docs_bot Makefile:
        make abi-load
    """
    import sys

    from naas_abi_core.engine.Engine import Engine

    # Boot the ABI engine using its standard config.yaml.
    # This starts Oxigraph (if not already running) and wires all services.
    engine = Engine()
    engine.load(module_names=["docsbot"])

    triple_store = engine.services.triple_store

    # Pull the graph path from the docsbot module configuration.
    from docsbot import ABIModule  # noqa: E402 — import after engine.load
    graph_path = ABIModule.get_instance().configuration.graph_path

    pipeline = LoadGraphPipeline(
        LoadGraphPipelineConfiguration(
            triple_store=triple_store,
            graph_path=graph_path,
        )
    )

    count = pipeline.run(LoadGraphPipelineParameters())
    if count == 0:
        sys.exit(1)
    print(f"✅ Loaded {count} triples into the triple store.")
