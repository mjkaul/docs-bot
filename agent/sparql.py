"""
SPARQL query functions for the DocsBot knowledge graph.

These are the same four queries as the ABI workflows in abi_module/docsbot/workflows/,
with two differences:

  1. No ABI wrapper classes (Workflow, Configuration, Parameters, StructuredTool).
     Just plain Python functions that take an rdflib Graph and return plain dicts.

  2. No FROM <named-graph> clause.
     In Oxigraph we stored triples in a named graph, so queries needed FROM.
     Here we load the TTL directly into rdflib's default graph, so no FROM needed.

Reading order for learning: read the corresponding ABI workflow file alongside
each function here to see exactly what the framework was doing around the query.
"""

from __future__ import annotations

from typing import Optional

from rdflib import Graph

# Shared SPARQL namespace prefixes — identical to the ABI workflow files.
SPARQL_PREFIXES = """
PREFIX docs:    <http://docsbot.local/ontology/>
PREFIX topic:   <http://docsbot.local/topic/>
PREFIX term:    <http://docsbot.local/term/>
PREFIX subject: <http://docsbot.local/subject/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX skos:    <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
"""

# The five topic classes we care about.  Used in FILTER(?type IN (...)) to exclude
# RDF meta-types like owl:NamedIndividual that every node implicitly carries.
TOPIC_CLASSES = """
    docs:ConceptTopic,
    docs:TaskTopic,
    docs:ReferenceTopic,
    docs:GlossaryEntry,
    docs:SectionTopic
"""


def find_tasks_for_term(g: Graph, term_id: str) -> list[dict]:
    """
    Return all TaskTopics that mention a given vocabulary term.

    A TaskTopic is a how-to procedure page.  A docs:mentions edge connects a
    topic to every glossary term that appears in its content (set by enrich_metadata.py).

    ABI equivalent: abi_module/docsbot/workflows/FindTasksWorkflow.py

    Args:
        g:       rdflib Graph loaded from graph/docs_graph.ttl.
        term_id: Glossary term slug, e.g. "statefulset" or "persistent-volume".

    Returns:
        List of {title, path, term_label} dicts.
    """
    term_uri = f"http://docsbot.local/term/{term_id}"

    sparql = SPARQL_PREFIXES + f"""
    SELECT ?title ?path ?term_label
    WHERE {{
        # Only task (how-to) topics, not concept or reference pages.
        ?task a docs:TaskTopic ;
              dcterms:title ?title ;
              docs:canonicalPath ?path ;
              docs:mentions <{term_uri}> .

        # Human-readable label for the term (e.g. "StatefulSet").
        OPTIONAL {{ <{term_uri}> skos:prefLabel ?term_label . }}
    }}
    ORDER BY ?title
    """

    rows = []
    for row in g.query(sparql):
        rows.append({
            "title": str(row["title"]) if row["title"] else None,
            "path": str(row["path"]) if row["path"] else None,
            "term_label": str(row["term_label"]) if row["term_label"] else term_id,
        })
    return rows


def impact_of_term(g: Graph, term_id: str, include_titles: bool = True) -> dict:
    """
    Blast-radius analysis: count how many topics (by type) mention a term.

    Run before renaming or redefining a term to understand the scope of work.

    ABI equivalent: abi_module/docsbot/workflows/ImpactAnalysisWorkflow.py

    Args:
        g:              rdflib Graph loaded from graph/docs_graph.ttl.
        term_id:        Glossary term slug, e.g. "pod".
        include_titles: If True, also return individual topic titles and paths.

    Returns:
        {
          "term_id":  "pod",
          "summary":  [{"type": "ConceptTopic", "count": 12}, ...],
          "topics":   [{"title": "...", "path": "...", "type": "..."}, ...]
        }
        "topics" is [] when include_titles=False.
    """
    term_uri = f"http://docsbot.local/term/{term_id}"

    # Query 1: count by topic type.
    # SPARQL GROUP BY works like SQL GROUP BY: aggregate one count per ?type value.
    count_sparql = SPARQL_PREFIXES + f"""
    SELECT ?type (COUNT(?topic) AS ?n)
    WHERE {{
        ?topic docs:mentions <{term_uri}> ;
               a ?type .
        FILTER(?type IN ({TOPIC_CLASSES}))
    }}
    GROUP BY ?type
    ORDER BY DESC(?n)
    """

    summary = []
    for row in g.query(count_sparql):
        # ?type is a full URI like <http://docsbot.local/ontology/ConceptTopic>.
        # We extract just the local name after the last "/" for readability.
        type_label = str(row["type"]).split("/")[-1] if row["type"] else ""
        summary.append({
            "type": type_label,
            "count": int(str(row["n"])) if row["n"] else 0,
        })

    # Query 2: individual topics (optional, so we skip it when not requested).
    topics: list[dict] = []
    if include_titles:
        detail_sparql = SPARQL_PREFIXES + f"""
        SELECT ?title ?path ?type
        WHERE {{
            ?topic docs:mentions <{term_uri}> ;
                   a ?type ;
                   dcterms:title ?title ;
                   docs:canonicalPath ?path .
            FILTER(?type IN ({TOPIC_CLASSES}))
        }}
        ORDER BY ?type ?title
        """
        for row in g.query(detail_sparql):
            topics.append({
                "title": str(row["title"]) if row["title"] else None,
                "path": str(row["path"]) if row["path"] else None,
                "type": str(row["type"]).split("/")[-1] if row["type"] else "",
            })

    return {"term_id": term_id, "summary": summary, "topics": topics}


def topics_by_subject(
    g: Graph,
    subject_id: str,
    topic_type: Optional[str] = None,
) -> list[dict]:
    """
    List all topics tagged with a taxonomy subject (e.g. "storage", "networking").

    The taxonomy subjects come from taxonomy/taxonomy.yaml.  During enrichment,
    each topic inherits subjects from the glossary terms it mentions.

    ABI equivalent: abi_module/docsbot/workflows/TopicsBySubjectWorkflow.py

    Args:
        g:          rdflib Graph loaded from graph/docs_graph.ttl.
        subject_id: Taxonomy subject slug, e.g. "storage", "networking".
        topic_type: Optional filter to a specific class, e.g. "TaskTopic".

    Returns:
        List of {title, path, type, subject_label} dicts.
    """
    subject_uri = f"http://docsbot.local/subject/{subject_id}"

    # Optional filter — restrict to one topic type if requested.
    type_extra = f"FILTER(?type = docs:{topic_type})" if topic_type else ""

    sparql = SPARQL_PREFIXES + f"""
    SELECT DISTINCT ?title ?path ?type ?subject_label
    WHERE {{
        ?topic docs:hasSubject <{subject_uri}> ;
               dcterms:title ?title ;
               docs:canonicalPath ?path ;
               a ?type .

        # Exclude RDF meta-types; keep only our five topic classes.
        FILTER(?type IN ({TOPIC_CLASSES}))

        {type_extra}

        OPTIONAL {{ <{subject_uri}> skos:prefLabel ?subject_label . }}
    }}
    ORDER BY ?type ?title
    """

    rows = []
    for row in g.query(sparql):
        rows.append({
            "title": str(row["title"]) if row["title"] else None,
            "path": str(row["path"]) if row["path"] else None,
            "type": str(row["type"]).split("/")[-1] if row["type"] else None,
            "subject_label": str(row["subject_label"]) if row["subject_label"] else subject_id,
        })
    return rows


def orphan_topics(
    g: Graph,
    topic_type: str = "ConceptTopic",
    limit: int = 50,
) -> list[dict]:
    """
    Find topics that no other topic links to (no inbound docs:references edges).

    Orphans are either legitimate entry-points or content gaps — pages that
    exist but aren't woven into the doc structure via cross-references.

    SPARQL technique: FILTER NOT EXISTS is the RDF equivalent of a SQL
    LEFT JOIN ... WHERE right_side IS NULL.

    ABI equivalent: abi_module/docsbot/workflows/OrphanTopicsWorkflow.py

    Args:
        g:          rdflib Graph loaded from graph/docs_graph.ttl.
        topic_type: Class to check: "ConceptTopic", "TaskTopic", "ReferenceTopic".
        limit:      Maximum number of results.

    Returns:
        List of {title, path} dicts.
    """
    sparql = SPARQL_PREFIXES + f"""
    SELECT ?title ?path
    WHERE {{
        ?topic a docs:{topic_type} ;
               dcterms:title ?title ;
               docs:canonicalPath ?path .

        # Only include topics for which there is NO inbound reference edge.
        FILTER NOT EXISTS {{ ?other docs:references ?topic . }}
    }}
    ORDER BY ?title
    LIMIT {limit}
    """

    rows = []
    for row in g.query(sparql):
        rows.append({
            "title": str(row["title"]) if row["title"] else None,
            "path": str(row["path"]) if row["path"] else None,
        })
    return rows
