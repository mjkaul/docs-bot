#!/usr/bin/env python3
"""
DocsBot — knowledge-graph-grounded chat agent for Kubernetes documentation.

Usage:
    python docsbot.py                              # interactive REPL
    python docsbot.py "Which tasks mention pod?"   # single question, then exit

How it works:
    1. graph/docs_graph.ttl is loaded into an in-memory rdflib Graph (~3 000 triples).
    2. Four SPARQL query functions are exposed to Claude as tools (Claude API tool-use).
    3. Claude reads your question, decides which tool(s) to call, runs them against
       the graph, then writes a grounded answer citing real page titles and paths.

No server required.  The entire graph lives in Python process memory.

Environment:
    ANTHROPIC_API_KEY — required.  Set in .env or export in your shell.

Setup (one-time):
    pip install -r requirements.txt   # or: make install
    cp .env.example .env && $EDITOR .env   # paste your key
    make graph                        # build graph/docs_graph.ttl from content/
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from rdflib import Graph

from agent.sparql import (
    find_tasks_for_term,
    impact_of_term,
    orphan_topics,
    topics_by_subject,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

load_dotenv()  # reads .env if present; doesn't override real env vars

GRAPH_PATH = Path(__file__).parent / "graph" / "docs_graph.ttl"

# claude-sonnet-4-5 is capable enough to reason over tool results and write
# grounded prose; use claude-opus-4-8 if you want deeper synthesis.
MODEL = "claude-sonnet-4-5"

# ---------------------------------------------------------------------------
# Tool definitions (Claude API format)
# ---------------------------------------------------------------------------
# The `tools` list tells Claude what functions it can call and what arguments
# they accept.  Claude uses the description and input_schema to decide when and
# how to call each tool — so descriptions should read like good docstrings.
#
# Compare this to the abi_module approach where tools are declared as
# LangChain StructuredTool objects.  The Claude API format is just JSON — no
# framework dependency needed.

TOOLS: list[dict] = [
    {
        "name": "find_tasks_for_term",
        "description": (
            "Find all task (how-to) topics in the Kubernetes documentation that "
            "mention a specific glossary term via a knowledge-graph edge.  "
            "Use this for questions like 'Which how-to pages cover StatefulSets?' "
            "or 'What tasks mention persistent volumes?'"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "term_id": {
                    "type": "string",
                    "description": (
                        "Glossary term slug — lowercase, hyphen-separated.  "
                        "Examples: 'statefulset', 'pod', 'persistent-volume', "
                        "'node', 'deployment', 'service'."
                    ),
                }
            },
            "required": ["term_id"],
        },
    },
    {
        "name": "impact_of_term",
        "description": (
            "Analyse the blast radius of changing a vocabulary term: returns a "
            "count of how many documentation topics (grouped by type: ConceptTopic, "
            "TaskTopic, etc.) mention it, plus an optional list of individual titles.  "
            "Use this before renaming or redefining a term, or to answer 'How widely "
            "used is X across the docs?'"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "term_id": {
                    "type": "string",
                    "description": "Glossary term slug, e.g. 'pod', 'node', 'deployment'.",
                },
                "include_titles": {
                    "type": "boolean",
                    "description": (
                        "If true (default), return individual topic titles alongside "
                        "the per-type counts.  Set false for a faster summary-only result."
                    ),
                    "default": True,
                },
            },
            "required": ["term_id"],
        },
    },
    {
        "name": "topics_by_subject",
        "description": (
            "List all documentation topics tagged with a taxonomy subject area such as "
            "'storage', 'networking', 'security', or 'workload'.  Optionally filter to "
            "a specific topic type (e.g. only how-to tasks).  Use for questions like "
            "'Show me all storage-related concept pages' or 'What tasks cover networking?'"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "subject_id": {
                    "type": "string",
                    "description": (
                        "Taxonomy subject slug — lowercase, hyphen-separated.  "
                        "Examples: 'storage', 'networking', 'security', 'workload', "
                        "'scheduling', 'cluster-administration', 'configuration'."
                    ),
                },
                "topic_type": {
                    "type": "string",
                    "description": (
                        "Optional topic-type filter.  One of: 'ConceptTopic', 'TaskTopic', "
                        "'ReferenceTopic', 'GlossaryEntry', 'SectionTopic'.  "
                        "Omit to return all types."
                    ),
                },
            },
            "required": ["subject_id"],
        },
    },
    {
        "name": "orphan_topics",
        "description": (
            "Find documentation topics that no other topic links to — topics with no "
            "inbound 'references' edges in the knowledge graph.  Useful for identifying "
            "content gaps or isolated pages that need cross-referencing."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "topic_type": {
                    "type": "string",
                    "description": (
                        "Topic class to check for orphans.  One of: 'ConceptTopic' "
                        "(default), 'TaskTopic', 'ReferenceTopic'."
                    ),
                    "default": "ConceptTopic",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of orphan topics to return.  Default: 50.",
                    "default": 50,
                },
            },
            "required": [],
        },
    },
]

# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------

def dispatch_tool(g: Graph, name: str, tool_input: dict) -> str:
    """
    Call the requested SPARQL function and return its result as a JSON string.

    Claude sends back tool_use blocks with a `name` and `input` dict.
    We route those to the matching function in agent/sparql.py, run it
    against the in-memory rdflib Graph, and serialize the result to JSON
    so Claude can read it in the next turn.

    Args:
        g:          The in-memory rdflib Graph.
        name:       Tool name Claude requested (must match a key in TOOLS).
        tool_input: Dict of arguments Claude chose for this call.

    Returns:
        JSON string — the tool result Claude will read.
    """
    if name == "find_tasks_for_term":
        result = find_tasks_for_term(g, **tool_input)
    elif name == "impact_of_term":
        result = impact_of_term(g, **tool_input)
    elif name == "topics_by_subject":
        result = topics_by_subject(g, **tool_input)
    elif name == "orphan_topics":
        result = orphan_topics(g, **tool_input)
    else:
        result = {"error": f"Unknown tool: {name}"}

    return json.dumps(result, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are DocsBot, an assistant that answers questions about Ray documentation "
    "using a structured knowledge graph built from the official Ray docs "
    "(ray-project/ray, Apache 2.0).\n\n"
    "The graph covers: Ray Core, Ray Serve, Ray Train, Ray Tune, Ray Data, and "
    "Ray Observability.  Taxonomy subjects are: core, serve, train, tune, data, "
    "observability, cluster.\n\n"
    "When the user asks about documentation topics, terms, or subject areas, "
    "use your tools to query the graph and ground every claim in real data.  "
    "Always cite specific page titles and canonical paths from tool results.  "
    "If a tool returns no results, say so — do not guess or hallucinate content."
)


def ask(client: anthropic.Anthropic, g: Graph, question: str) -> str:
    """
    Send one question through the Claude tool-use loop and return the final answer.

    The agentic loop:
      1. POST user message + tool definitions → Claude.
      2. Claude may respond with tool_use blocks (stop_reason = "tool_use").
         For each, call dispatch_tool() and collect the result.
      3. POST tool results back as tool_result content blocks.
      4. Repeat until Claude stops with stop_reason = "end_turn" (text-only response).

    This is the standard Claude tool-use pattern.  Each iteration adds to the
    `messages` list so Claude has full conversation history at every step.

    Args:
        client:   Anthropic client (holds the API key).
        g:        rdflib Graph (shared across all calls in one session).
        question: User's natural-language question.

    Returns:
        Claude's final text response.
    """
    messages: list[dict] = [{"role": "user", "content": question}]

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,           # type: ignore[arg-type]
            messages=messages,     # type: ignore[arg-type]
        )

        # Append Claude's response to history — required by the API so each
        # subsequent call can see what Claude said previously.
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # Claude is done reasoning and tool-calling.  Extract final text.
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return ""  # shouldn't happen, but be safe

        if response.stop_reason == "tool_use":
            # Claude wants to call one or more tools.
            # Collect all tool_use blocks from this response turn.
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"  → {block.name}({json.dumps(block.input)})", flush=True)
                    result_str = dispatch_tool(g, block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,   # links result to the specific tool call
                        "content": result_str,
                    })

            # Send all tool results back in one user turn, then loop again.
            messages.append({"role": "user", "content": tool_results})

        else:
            # Unexpected stop reason — return whatever text is available.
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return f"[stopped: {response.stop_reason}]"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    # --- validate environment -----------------------------------------------
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            "ERROR: ANTHROPIC_API_KEY is not set.\n"
            "  Copy .env.example to .env and paste your key, or:\n"
            "  export ANTHROPIC_API_KEY=sk-ant-..."
        )
        sys.exit(1)

    if not GRAPH_PATH.exists():
        print(
            f"ERROR: {GRAPH_PATH} not found.\n"
            "  Run 'make graph' to build the knowledge graph first."
        )
        sys.exit(1)

    # --- load graph ---------------------------------------------------------
    print(f"Loading {GRAPH_PATH} ...", flush=True)
    g = Graph()
    g.parse(GRAPH_PATH, format="turtle")
    print(f"Loaded {len(g):,} triples.\n", flush=True)

    client = anthropic.Anthropic(api_key=api_key)

    # --- single-question mode (CLI arg) ------------------------------------
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        print(f"Q: {question}\n")
        answer = ask(client, g, question)
        print(f"A: {answer}\n")
        return

    # --- interactive REPL --------------------------------------------------
    print("DocsBot ready. Ask a question about the Kubernetes docs, or type 'quit'.\n")
    while True:
        try:
            question = input("Q: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Bye.")
            break

        answer = ask(client, g, question)
        print(f"\nA: {answer}\n")


if __name__ == "__main__":
    main()
