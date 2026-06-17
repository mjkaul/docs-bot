"""
OrphanTopicsWorkflow — "Which topics is nothing linking to?"

An orphan is a topic that no other topic references (no inbound docs:references
edges).  Orphans are either:
  - Legitimate entry points (top-level pages that don't need to be linked from
    another page), or
  - Content gaps — pages that exist but aren't woven into the doc structure.

This query uses SPARQL's FILTER NOT EXISTS clause, which is the RDF equivalent
of a SQL LEFT JOIN ... WHERE right_side IS NULL (i.e. "find subjects for which
the pattern does NOT hold").

Scoping to ConceptTopics only (the default) keeps the list useful: section
index pages and glossary entries are expected to be sparse on inbound links.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Optional

from langchain_core.tools import BaseTool, StructuredTool
from naas_abi_core.services.triple_store.TripleStorePorts import ITripleStoreService
from naas_abi_core.utils.Expose import APIRouter
from naas_abi_core.workflow import Workflow, WorkflowConfiguration
from naas_abi_core.workflow.workflow import WorkflowParameters
from pydantic import Field
from rdflib import query as rdflib_query

SPARQL_PREFIXES = """
PREFIX docs:    <http://docsbot.local/ontology/>
PREFIX dcterms: <http://purl.org/dc/terms/>
"""

DOCSBOT_GRAPH = "http://docsbot.local/graph/docs"


@dataclass
class OrphanTopicsWorkflowConfiguration(WorkflowConfiguration):
    triple_store: ITripleStoreService


class OrphanTopicsWorkflowParameters(WorkflowParameters):
    """
    Attributes:
        topic_type: Which class of topics to check for orphans.
                    Defaults to "ConceptTopic" — the most informative orphan check.
        limit:      Cap the result set to avoid overwhelming the agent context.
    """
    topic_type: Annotated[
        str,
        Field(
            description=(
                "Topic type to check for orphans. One of: 'ConceptTopic', "
                "'TaskTopic', 'ReferenceTopic'. Default: 'ConceptTopic'."
            ),
            default="ConceptTopic",
        ),
    ] = "ConceptTopic"
    limit: Annotated[
        int,
        Field(
            description="Maximum number of orphan topics to return. Default: 50.",
            ge=1,
            le=500,
            default=50,
        ),
    ] = 50


class OrphanTopicsWorkflow(Workflow):
    """Find topics that no other topic links to."""

    __configuration: OrphanTopicsWorkflowConfiguration

    def __init__(self, configuration: OrphanTopicsWorkflowConfiguration) -> None:
        super().__init__(configuration)
        self.__configuration = configuration

    def orphan_topics(self, parameters: OrphanTopicsWorkflowParameters) -> list[dict]:
        """Return topics of the requested type that have zero inbound references.

        Args:
            parameters: topic_type and limit.

        Returns:
            List of dicts: title, path.
        """
        sparql = SPARQL_PREFIXES + f"""
        SELECT ?title ?path
        FROM <{DOCSBOT_GRAPH}>
        WHERE {{
            # The candidate topic must be of the requested type.
            ?topic a docs:{parameters.topic_type} ;
                   dcterms:title ?title ;
                   docs:canonicalPath ?path .

            # FILTER NOT EXISTS: include only topics for which there is NO
            # triple of the form (?other docs:references ?topic).
            # This is the graph equivalent of "no inbound links".
            FILTER NOT EXISTS {{
                ?other docs:references ?topic .
            }}
        }}
        ORDER BY ?title
        LIMIT {parameters.limit}
        """

        results = self.__configuration.triple_store.query(sparql)
        rows = []
        for row in results:
            assert isinstance(row, rdflib_query.ResultRow)
            rows.append({
                "title": str(row["title"]) if row["title"] else None,
                "path": str(row["path"]) if row["path"] else None,
            })
        return rows

    def as_tools(self) -> list[BaseTool]:
        return [
            StructuredTool(
                name="orphan_topics",
                description=(
                    "Find documentation topics that no other topic links to "
                    "(no inbound 'references' edges in the graph).  Useful for "
                    "identifying content gaps or pages that need better integration "
                    "into the doc structure."
                ),
                func=lambda **kwargs: self.orphan_topics(
                    OrphanTopicsWorkflowParameters(**kwargs)
                ),
                args_schema=OrphanTopicsWorkflowParameters,
            )
        ]

    def as_api(self, router, route_name="", name="", description="",
               description_stream="", tags=None) -> None:
        return None
