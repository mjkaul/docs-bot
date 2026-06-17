"""
TopicsBySubjectWorkflow — "Show me all topics tagged with subject X."

The taxonomy (taxonomy.yaml) defines subjects like "networking", "storage",
"security".  The enrichment step tags each topic with the subjects inherited
from the glossary terms it mentions.  This workflow exposes that tagging as a
queryable index.

Use-case: a writer responsible for the "storage" section of the docs can ask
"which topics are tagged storage?" to get a full inventory of their area.
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
PREFIX subject: <http://docsbot.local/subject/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX skos:    <http://www.w3.org/2004/02/skos/core#>
"""

DOCSBOT_GRAPH = "http://docsbot.local/graph/docs"


@dataclass
class TopicsBySubjectWorkflowConfiguration(WorkflowConfiguration):
    triple_store: ITripleStoreService


class TopicsBySubjectWorkflowParameters(WorkflowParameters):
    """
    Attributes:
        subject_id: Taxonomy subject slug, e.g. "storage", "networking".
                    Must match an `id` in taxonomy.yaml.
        topic_type: Optional filter to a specific topic type class name,
                    e.g. "TaskTopic", "ConceptTopic".  Pass None for all types.
    """
    subject_id: Annotated[
        str,
        Field(
            description=(
                "Taxonomy subject slug (lowercase, hyphen-separated). "
                "Examples: 'storage', 'networking', 'security', 'workload'."
            ),
            example="storage",
        ),
    ]
    topic_type: Annotated[
        Optional[str],
        Field(
            description=(
                "Optional topic type filter. One of: 'ConceptTopic', 'TaskTopic', "
                "'ReferenceTopic', 'GlossaryEntry', 'SectionTopic'. "
                "Omit to return all types."
            ),
            default=None,
        ),
    ] = None


class TopicsBySubjectWorkflow(Workflow):
    """List all topics tagged with a given taxonomy subject."""

    __configuration: TopicsBySubjectWorkflowConfiguration

    def __init__(self, configuration: TopicsBySubjectWorkflowConfiguration) -> None:
        super().__init__(configuration)
        self.__configuration = configuration

    def topics_by_subject(self, parameters: TopicsBySubjectWorkflowParameters) -> list[dict]:
        """Return topics tagged with the requested subject.

        Args:
            parameters: subject_id and optional topic_type filter.

        Returns:
            List of dicts: title, path, type, subject_label.
        """
        subject_uri = f"http://docsbot.local/subject/{parameters.subject_id}"

        # Build an optional FILTER clause if the caller requested a specific type.
        type_filter = ""
        if parameters.topic_type:
            type_filter = f"?topic a docs:{parameters.topic_type} ."
        else:
            # Still bind ?type so we can include it in the result.
            type_filter = "?topic a ?type ."

        sparql = SPARQL_PREFIXES + f"""
        SELECT DISTINCT ?title ?path ?type ?subject_label
        FROM <{DOCSBOT_GRAPH}>
        WHERE {{
            # Every topic has a docs:hasSubject edge to a subject node.
            ?topic docs:hasSubject <{subject_uri}> ;
                   dcterms:title ?title ;
                   docs:canonicalPath ?path ;
                   a ?type .

            # FILTER to exclude RDF meta-types (owl:Class, etc.) from ?type.
            FILTER(?type IN (
                docs:ConceptTopic,
                docs:TaskTopic,
                docs:ReferenceTopic,
                docs:GlossaryEntry,
                docs:SectionTopic
            ))

            {type_filter}

            # Human-readable subject label (e.g. "Storage").
            OPTIONAL {{ <{subject_uri}> skos:prefLabel ?subject_label . }}
        }}
        ORDER BY ?type ?title
        """

        results = self.__configuration.triple_store.query(sparql)
        rows = []
        for row in results:
            assert isinstance(row, rdflib_query.ResultRow)
            rows.append({
                "title": str(row["title"]) if row["title"] else None,
                "path": str(row["path"]) if row["path"] else None,
                "type": str(row["type"]).split("/")[-1] if row["type"] else None,
                "subject_label": str(row["subject_label"]) if row["subject_label"] else parameters.subject_id,
            })
        return rows

    def as_tools(self) -> list[BaseTool]:
        return [
            StructuredTool(
                name="topics_by_subject",
                description=(
                    "List all documentation topics tagged with a taxonomy subject "
                    "(e.g. 'storage', 'networking', 'security').  Optionally filter "
                    "to a specific topic type.  Useful for inventorying coverage of "
                    "a subject area."
                ),
                func=lambda **kwargs: self.topics_by_subject(
                    TopicsBySubjectWorkflowParameters(**kwargs)
                ),
                args_schema=TopicsBySubjectWorkflowParameters,
            )
        ]

    def as_api(self, router, route_name="", name="", description="",
               description_stream="", tags=None) -> None:
        return None
