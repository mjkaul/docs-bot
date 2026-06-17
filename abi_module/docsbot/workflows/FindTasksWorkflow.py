"""
FindTasksWorkflow — "Which task topics mention term X?"

This is the most common docs-graph query: given a vocabulary term (e.g.
"statefulset"), find every TaskTopic that uses that term via a
docs:mentions edge.  The result tells a technical writer which how-to pages
need updating if the term's meaning changes.

SPARQL background
-----------------
A SPARQL SELECT query works like SQL: we describe a *pattern* of RDF triples
and ask for every assignment of variables that makes the pattern true.

    ?task  a  docs:TaskTopic         — ?task is typed as a TaskTopic
    ?task  docs:mentions  ?term_uri  — ?task has a mentions edge to ?term_uri

RDF stores match these patterns over their triple index and return rows
where every variable is bound to a real node in the graph.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from langchain_core.tools import BaseTool, StructuredTool
from naas_abi_core.services.triple_store.TripleStorePorts import ITripleStoreService
from naas_abi_core.utils.Expose import APIRouter
from naas_abi_core.workflow import Workflow, WorkflowConfiguration
from naas_abi_core.workflow.workflow import WorkflowParameters
from pydantic import Field
from rdflib import query as rdflib_query


# ---------------------------------------------------------------------------
# Namespaces shared across all docsbot SPARQL queries.
# ---------------------------------------------------------------------------

# These PREFIX declarations translate short names to full URIs so our SPARQL
# doesn't have to repeat the full URI every time.
SPARQL_PREFIXES = """
PREFIX docs:    <http://docsbot.local/ontology/>
PREFIX topic:   <http://docsbot.local/topic/>
PREFIX term:    <http://docsbot.local/term/>
PREFIX subject: <http://docsbot.local/subject/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX skos:    <http://www.w3.org/2004/02/skos/core#>
"""

# Named graph where LoadGraphPipeline stored the docsbot triples.
# All queries must include FROM <DOCSBOT_GRAPH> so they hit the right
# graph in Oxigraph's quad store rather than the (empty) default graph.
DOCSBOT_GRAPH = "http://docsbot.local/graph/docs"


# ---------------------------------------------------------------------------
# Configuration — injected at construction time
# ---------------------------------------------------------------------------

@dataclass
class FindTasksWorkflowConfiguration(WorkflowConfiguration):
    """
    Attributes:
        triple_store: The ABI triple store service backed by Oxigraph.
    """
    triple_store: ITripleStoreService


# ---------------------------------------------------------------------------
# Parameters — provided when the agent calls this workflow as a tool
# ---------------------------------------------------------------------------

class FindTasksWorkflowParameters(WorkflowParameters):
    """
    Attributes:
        term_id: The slug of the glossary term to search for, e.g. "statefulset".
                 This matches the `id` field in the glossary frontmatter, which
                 becomes the local name of the term URI:
                 <http://docsbot.local/term/statefulset>.
    """
    term_id: Annotated[
        str,
        Field(
            description=(
                "Glossary term slug to search for (lowercase, hyphen-separated). "
                "Examples: 'statefulset', 'pod', 'persistent-volume'."
            ),
            example="statefulset",
        ),
    ]


# ---------------------------------------------------------------------------
# Workflow implementation
# ---------------------------------------------------------------------------

class FindTasksWorkflow(Workflow):
    """Return all TaskTopics that mention a given vocabulary term."""

    __configuration: FindTasksWorkflowConfiguration

    def __init__(self, configuration: FindTasksWorkflowConfiguration) -> None:
        super().__init__(configuration)
        self.__configuration = configuration

    def find_tasks(self, parameters: FindTasksWorkflowParameters) -> list[dict]:
        """Run the SPARQL query and return matching task topics.

        Args:
            parameters: Contains the term_id to search for.

        Returns:
            List of dicts with keys: title, path, term_label.
        """
        # Build the full term URI from the slug.
        # e.g. "statefulset" → <http://docsbot.local/term/statefulset>
        term_uri = f"http://docsbot.local/term/{parameters.term_id}"

        sparql = SPARQL_PREFIXES + f"""
        SELECT ?title ?path ?term_label
        FROM <{DOCSBOT_GRAPH}>
        WHERE {{
            # The topic must be typed as a TaskTopic (a how-to procedure).
            ?task a docs:TaskTopic ;
                  dcterms:title ?title ;
                  docs:canonicalPath ?path ;
                  docs:mentions <{term_uri}> .

            # Also fetch the human-readable label of the term itself.
            OPTIONAL {{ <{term_uri}> skos:prefLabel ?term_label . }}
        }}
        ORDER BY ?title
        """

        results = self.__configuration.triple_store.query(sparql)

        rows = []
        for row in results:
            assert isinstance(row, rdflib_query.ResultRow)
            rows.append({
                "title": str(row["title"]) if row["title"] else None,
                "path": str(row["path"]) if row["path"] else None,
                "term_label": str(row["term_label"]) if row["term_label"] else parameters.term_id,
            })
        return rows

    def as_tools(self) -> list[BaseTool]:
        """Return this workflow as a LangChain tool the agent can call."""
        return [
            StructuredTool(
                name="find_tasks_for_term",
                description=(
                    "Find all task (how-to) topics in the documentation that mention "
                    "a specific vocabulary term.  Useful for questions like 'which "
                    "procedures involve StatefulSets?'."
                ),
                func=lambda **kwargs: self.find_tasks(
                    FindTasksWorkflowParameters(**kwargs)
                ),
                args_schema=FindTasksWorkflowParameters,
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
        return None
