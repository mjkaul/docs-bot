#!/usr/bin/env python3
"""Convert enriched corpus to RDF (Iantosca steps 3-4).

Reads ontology/docs_ontology.ttl + content/enriched/, emits graph/docs_graph.ttl:
topics typed by topic_type, SKOS subjects/terms, mentions/references/partOf edges.
Internal /docs/ links are resolved to topic nodes when the target is in the corpus.
"""
from pathlib import Path

import frontmatter
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import DCTERMS, SKOS

ROOT = Path(__file__).resolve().parent.parent
ENRICHED = ROOT / "content" / "enriched"
OUT = ROOT / "graph" / "docs_graph.ttl"

DOCS = Namespace("http://docsbot.local/ontology/")
TOPIC = Namespace("http://docsbot.local/topic/")
TERM = Namespace("http://docsbot.local/term/")
SUBJ = Namespace("http://docsbot.local/subject/")

CLASS_FOR_TYPE = {
    "concept": DOCS.ConceptTopic,
    "task": DOCS.TaskTopic,
    "reference": DOCS.ReferenceTopic,
    "glossary_term": DOCS.GlossaryEntry,
    "section": DOCS.SectionTopic,
}


def main() -> None:
    g = Graph()
    g.parse(ROOT / "ontology" / "docs_ontology.ttl")
    for prefix, ns in [("docs", DOCS), ("topic", TOPIC), ("term", TERM), ("subject", SUBJ)]:
        g.bind(prefix, ns)

    posts = {}
    path_index = {}  # canonical_path -> topic URI
    for f in sorted(ENRICHED.rglob("*.md")):
        post = frontmatter.load(f)
        uri = TOPIC[post["id"]]
        posts[uri] = post
        path_index[post["canonical_path"].rstrip("/")] = uri

    scheme = SUBJ["scheme"]
    g.add((scheme, RDF.type, SKOS.ConceptScheme))
    g.add((scheme, SKOS.prefLabel, Literal("docs_bot subject taxonomy")))

    for uri, post in posts.items():
        ttype = post["topic_type"]
        g.add((uri, RDF.type, CLASS_FOR_TYPE[ttype]))
        g.add((uri, DCTERMS.title, Literal(post["title"])))
        g.add((uri, DOCS.topicId, Literal(post["id"])))
        g.add((uri, DOCS.canonicalPath, Literal(post["canonical_path"])))
        g.add((uri, DCTERMS.source, URIRef(post["source"])))
        if post.get("description"):
            g.add((uri, DCTERMS.description, Literal(post["description"])))

        for s in post.get("subjects") or []:
            s_uri = SUBJ[s.replace(" ", "-").lower()]
            g.add((s_uri, RDF.type, DOCS.Subject))
            g.add((s_uri, SKOS.prefLabel, Literal(s)))
            g.add((s_uri, SKOS.inScheme, scheme))
            g.add((uri, DOCS.hasSubject, s_uri))

        for m in post.get("mentions") or []:
            t_uri = TERM[m]
            g.add((t_uri, RDF.type, DOCS.Term))
            g.add((t_uri, SKOS.prefLabel, Literal(m.replace("-", " "))))
            g.add((uri, DOCS.mentions, t_uri))

        if ttype == "glossary_term" and post.get("term_id"):
            t_uri = TERM[post["term_id"]]
            g.add((t_uri, RDF.type, DOCS.Term))
            g.add((uri, DOCS.defines, t_uri))
            if post.get("description"):
                g.add((t_uri, SKOS.definition, Literal(post["description"])))

        for ref in post.get("references") or []:
            target = path_index.get(ref.rstrip("/"))
            if target is not None and target != uri:
                g.add((uri, DOCS.references, target))

        # partOf: nearest ancestor section by id prefix
        parts = post["id"].split(".")
        for i in range(len(parts) - 1, 0, -1):
            parent = TOPIC[".".join(parts[:i])]
            if parent in posts and posts[parent]["topic_type"] == "section":
                g.add((uri, DOCS.partOf, parent))
                break

    OUT.parent.mkdir(exist_ok=True)
    g.serialize(OUT, format="turtle")
    print(f">> {len(g)} triples -> {OUT.relative_to(ROOT)}")
    print(f">> topics: {len(posts)}, resolved internal references: "
          f"{sum(1 for _ in g.triples((None, DOCS.references, None)))}, "
          f"mention edges: {sum(1 for _ in g.triples((None, DOCS.mentions, None)))}")


if __name__ == "__main__":
    main()
