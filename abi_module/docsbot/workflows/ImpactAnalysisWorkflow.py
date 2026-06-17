"""
ImpactAnalysisWorkflow — "If we change term X, what's the blast radius?"

This is the killer use-case for a knowledge graph over a plain doc site:
before renaming or redefining a term, you can ask the graph exactly which
topics reference it — grouped by topic type — so you know the scope of work.

The query uses a SPARQL aggregate (GROUP BY + COUNT) to tally how many topics
of each type mention the term, then a second query fetches the full list so
the agent can show specific titles and Confluence paths.
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

SPARQL_PREFIXES = """
PREFIX docs:    <http://docsbot.local/ontology/>
PREFIX topic:   <http://docsbot.local/topic/>
PREFIX term:    <http://docsbot.local/term/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
"""

DOCSBOT_GRAPH = "http://docsbot.local/graph/docs"


@dataclass
class ImpactAnalysisWorkflowConfiguration(WorkflowConfiguration):
    triple_store: ITripleStoreService


class ImpactAnalysisWorkflowParameters(WorkflowParameters):
    """
    Attributes:
        term_id: Slug of the term whose impact we're analysing, e.g. "pod".
        include_titles: When True, return individual topic titles in addition
                        to the per-type counts.  False gives a faster summary.
    """
    term_id: Annotated[
        str,
        Field(
            description=(
                "Glossary term slug to analyse (lowercase, hyphen-separated). "
                "Example: 'pod', 'node', 'deployment'."
            ),
            example="pod",
        ),
    ]
    include_titles: Annotated[
        bool,
        Field(
            description="If True, include individual topic titles alongside counts.",
            default=True,
        ),
    ] = True


class ImpactAnalysisWorkflow(Workflow):
    """Report how many topics (and which ones) mention a given term."""

    __configuration: ImpactAnalysisWorkflowConfiguration

    def __init__(self, configuration: ImpactAnalysisWorkflowConfiguration) -> None:
        super().__init__(configuration)
        self.__configuration = configuration

    def impact_of_term(self, parameters: ImpactAnalysisWorkflowParameters) -> dict:
        """Run two SPARQL queries: a COUNT summary and (optionally) full details.

        Returns:
            {
              "term_id": "pod",
              "summary": [{"type": "ConceptTopic", "count": 12}, ...],
              "topics": [{"title": "...", "path": "...", "type": "..."}, ...]
              # topics is [] when include_titles=False
            }
        """
        term_uri = f"http://docsbot.local/term/{parameters.term_id}"

        # --- Query 1: count topics by type -----------------------------------
        # SPARQL GROUP BY works like SQL GROUP BY: for every distinct value of
        # ?type, count how many ?topic rows exist.
        count_sparql = SPARQL_PREFIXES + f"""
        SELECT ?type (COUNT(?topic) AS ?n)
        FROM <{DOCSBOT_GRAPH}>
        WHERE {{
            ?topic docs:mentions <{term_uri}> ;
                   a ?type .
            # Filter to only our custom topic classes (exclude owl:NamedIndividual
            # and other RDF meta-types that every node implicitly carries).
            FILTER(?type IN (
                docs:ConceptTopic,
                docs:TaskTopic,
                docs:ReferenceTopic,
                docs:GlossaryEntry,
                docs:SectionTopic
            ))
        }}
        GROUP BY ?type
        ORDER BY DESC(?n)
        """

        count_results = self.__configuration.triple_store.query(count_sparql)
        summary = []
        for row in count_results:
            assert isinstance(row, rdflib_query.ResultRow)
            # The ?type variable holds a full URI like
            # <http://docsbot.local/ontology/ConceptTopic>.
            # We extract just the local name (after the last /) for readability.
            type_uri = str(row["type"]) if row["type"] else ""
            type_label = type_uri.split("/")[-1]
            summary.append({
                "type": type_label,
                "count": int(str(row["n"])) if row["n"] else 0,
            })

        # --- Query 2: individual topics (optional) ---------------------------
        topics: list[dict] = []
        if parameters.include_titles:
            detail_sparql = SPARQL_PREFIXES + f"""
            SELECT ?title ?path ?type
            FROM <{DOCSBOT_GRAPH}>
            WHERE {{
                ?topic docs:mentions <{term_uri}> ;
                       a ?type ;
                       dcterms:title ?title ;
                       docs:canonicalPath ?path .
                FILTER(?type IN (
                    docs:ConceptTopic,
                    docs:TaskTopic,
                    docs:ReferenceTopic,
                    docs:GlossaryEntry,
                    docs:SectionTopic
                ))
            }}
            ORDER BY ?type ?title
            """
            detail_results = self.__configuration.triple_store.query(detail_sparql)
            for row in detail_results:
                assert isinstance(row, rdflib_query.ResultRow)
                type_label = str(row["type"]).split("/")[-1] if row["type"] else ""
                topics.append({
                    "title": str(row["title"]) if row["title"] else None,
                    "path": str(row["path"]) if row["path"] else None,
                    "type": type_label,
                })

        return {
            "term_id": parameters.term_id,
            "summary": summary,
            "topics": topics,
        }

    def as_tools(self) -> list[BaseTool]:
        return [
            StructuredTool(
                name="impact_of_term",
                description=(
                    "Analyse the blast radius of changing a vocabulary term: returns "
                    "a count of how many documentation topics (grouped by type) mention "
                    "it, plus an optional list of individual topic titles and paths.  "
                    "Use this before renaming or redefining a term."
                ),
                func=lambda **kwargs: self.impact_of_term(
                    ImpactAnalysisWorkflowParameters(**kwargs)
                ),
                args_schema=ImpactAnalysisWorkflowParameters,
            )
        ]

    def as_api(self, router, route_name="", name="", description="",
               description_stream="", tags=None) -> None:
        return None
