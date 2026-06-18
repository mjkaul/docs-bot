import { QueryEngine } from "@comunica/query-sparql-rdfjs";
import type { Store } from "n3";

const engine = new QueryEngine();

const PREFIXES = `
PREFIX docs:    <http://docsbot.local/ontology/>
PREFIX topic:   <http://docsbot.local/topic/>
PREFIX term:    <http://docsbot.local/term/>
PREFIX subject: <http://docsbot.local/subject/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX skos:    <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
`;

const TOPIC_CLASSES = `
    docs:ConceptTopic,
    docs:TaskTopic,
    docs:ReferenceTopic,
    docs:GlossaryEntry,
    docs:SectionTopic
`;

function str(val: unknown): string {
  if (val == null) return "";
  if (typeof val === "object" && "value" in (val as object))
    return (val as { value: string }).value;
  return String(val);
}

function localName(uri: string): string {
  return uri.split("/").pop() ?? uri;
}

export async function findTasksForTerm(
  store: Store,
  termId: string
): Promise<{ title: string; path: string; term_label: string }[]> {
  const termUri = `http://docsbot.local/term/${termId}`;
  const query = PREFIXES + `
SELECT ?title ?path ?term_label
WHERE {
  ?task a docs:TaskTopic ;
        dcterms:title ?title ;
        docs:canonicalPath ?path ;
        docs:mentions <${termUri}> .
  OPTIONAL { <${termUri}> skos:prefLabel ?term_label . }
}
ORDER BY ?title
`;
  const stream = await engine.queryBindings(query, { sources: [store] });
  const rows = await stream.toArray();
  return rows.map((b) => ({
    title: str(b.get("title")),
    path: str(b.get("path")),
    term_label: str(b.get("term_label")) || termId,
  }));
}

export async function impactOfTerm(
  store: Store,
  termId: string,
  includeTitles = true
): Promise<{
  term_id: string;
  summary: { type: string; count: number }[];
  topics: { title: string; path: string; type: string }[];
}> {
  const termUri = `http://docsbot.local/term/${termId}`;

  const countQuery = PREFIXES + `
SELECT ?type (COUNT(?topic) AS ?n)
WHERE {
  ?topic docs:mentions <${termUri}> ;
         a ?type .
  FILTER(?type IN (${TOPIC_CLASSES}))
}
GROUP BY ?type
ORDER BY DESC(?n)
`;
  const countStream = await engine.queryBindings(countQuery, { sources: [store] });
  const countRows = await countStream.toArray();
  const summary = countRows.map((b) => ({
    type: localName(str(b.get("type"))),
    count: parseInt(str(b.get("n")), 10) || 0,
  }));

  let topics: { title: string; path: string; type: string }[] = [];
  if (includeTitles) {
    const detailQuery = PREFIXES + `
SELECT ?title ?path ?type
WHERE {
  ?topic docs:mentions <${termUri}> ;
         a ?type ;
         dcterms:title ?title ;
         docs:canonicalPath ?path .
  FILTER(?type IN (${TOPIC_CLASSES}))
}
ORDER BY ?type ?title
`;
    const detailStream = await engine.queryBindings(detailQuery, { sources: [store] });
    const detailRows = await detailStream.toArray();
    topics = detailRows.map((b) => ({
      title: str(b.get("title")),
      path: str(b.get("path")),
      type: localName(str(b.get("type"))),
    }));
  }

  return { term_id: termId, summary, topics };
}

export async function topicsBySubject(
  store: Store,
  subjectId: string,
  topicType?: string
): Promise<{ title: string; path: string; type: string; subject_label: string }[]> {
  const subjectUri = `http://docsbot.local/subject/${subjectId}`;
  const typeFilter = topicType ? `FILTER(?type = docs:${topicType})` : "";

  const query = PREFIXES + `
SELECT DISTINCT ?title ?path ?type ?subject_label
WHERE {
  ?topic docs:hasSubject <${subjectUri}> ;
         dcterms:title ?title ;
         docs:canonicalPath ?path ;
         a ?type .
  FILTER(?type IN (${TOPIC_CLASSES}))
  ${typeFilter}
  OPTIONAL { <${subjectUri}> skos:prefLabel ?subject_label . }
}
ORDER BY ?type ?title
`;
  const stream = await engine.queryBindings(query, { sources: [store] });
  const rows = await stream.toArray();
  return rows.map((b) => ({
    title: str(b.get("title")),
    path: str(b.get("path")),
    type: localName(str(b.get("type"))),
    subject_label: str(b.get("subject_label")) || subjectId,
  }));
}

export async function orphanTopics(
  store: Store,
  topicType = "ConceptTopic",
  limit = 50
): Promise<{ title: string; path: string }[]> {
  const query = PREFIXES + `
SELECT ?title ?path
WHERE {
  ?topic a docs:${topicType} ;
         dcterms:title ?title ;
         docs:canonicalPath ?path .
  FILTER NOT EXISTS { ?other docs:references ?topic . }
}
ORDER BY ?title
LIMIT ${limit}
`;
  const stream = await engine.queryBindings(query, { sources: [store] });
  const rows = await stream.toArray();
  return rows.map((b) => ({
    title: str(b.get("title")),
    path: str(b.get("path")),
  }));
}
