"""
docsbot — ABI custom module for the docs-as-code knowledge graph.

This module plugs into the Naas ABI framework and exposes the docs knowledge
graph (built by the docs_bot pipeline) as a set of SPARQL-backed tools that
a chat agent can call at runtime.

How ABI loads this module
-------------------------
ABI's Engine reads config.yaml and imports each enabled module by its Python
package path (e.g. "docsbot"). It then calls on_load() once at startup and
on_initialized() after all modules and services are ready.

What this module contributes
----------------------------
- An OWL ontology (ontologies/docs_ontology.ttl) that extends ABI's BFO/CCO
  stack with documentation-specific classes and properties.
- A LoadGraphPipeline that bulk-loads docs_graph.ttl into Oxigraph.
- Four SPARQL workflows that the DocsBotAgent calls to answer questions.
- A DocsBotAgent that appears in the Naas chat UI.
"""

from dataclasses import dataclass

from naas_abi_core.module.Module import BaseModule, ModuleConfiguration, ModuleDependencies
from naas_abi_core.services.triple_store.TripleStoreService import TripleStoreService


class ABIModule(BaseModule):
    """The docsbot ABI module.

    ABI discovers this class automatically because the file is named __init__.py
    and the class is named ABIModule (the conventional name ABI looks for).
    """

    # Tell ABI's engine that this module requires the triple store service.
    # Must use the concrete TripleStoreService class (not the interface)
    # so the engine's access-control check passes.
    dependencies: ModuleDependencies = ModuleDependencies(
        modules=[],
        services=[TripleStoreService],
    )

    class Configuration(ModuleConfiguration):
        """
        Fields that map to config.yaml entries under this module's `config:` key.

        Example config.yaml entry:

            modules:
              - module: docsbot
                enabled: true
                config:
                  graph_path: "../docs_bot/graph/docs_graph.ttl"
        """

        # Filesystem path to the compiled RDF graph produced by `make graph`
        # in the docs_bot repo.  Can be absolute or relative to the ABI
        # working directory.
        graph_path: str = "graph/docs_graph.ttl"

    def on_initialized(self) -> None:
        """Called after all modules and services are fully loaded.

        This is the safe place to access self._engine.services because we know
        every other module has finished its on_load() by this point.

        We don't need to manually register workflows or pipelines here —
        ABI's agent loader wires them into DocsBotAgent.New() at chat time.
        We just log a confirmation so the startup output shows the module is live.
        """
        from naas_abi_core import logger

        triple_store = self._engine.services.triple_store
        logger.info(
            f"[docsbot] Module initialized. "
            f"Graph path: {self._configuration.graph_path}. "
            f"Triple store: {triple_store.__class__.__name__}."
        )
