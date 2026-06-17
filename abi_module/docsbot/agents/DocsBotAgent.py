"""
DocsBotAgent — the chat agent that the Naas workspace exposes to users.

This agent appears in the Naas chat UI alongside any other ABI agents.
When a user asks a question, the agent decides which workflow tool to call,
calls it (getting back deterministic results from the graph), and then
uses the LLM only to phrase a readable answer — not to invent facts.

That division of labour is the core of the neuro-symbolic approach:
  - Symbolic layer (the graph + SPARQL): supplies facts with certainty
  - Neural layer (the LLM): translates facts into natural language

System prompt design
--------------------
The system prompt explains the ontology schema so the agent knows which
tool to call for each type of question.  The [TOOLS] placeholder is filled
at construction time with the actual list of registered tools so the prompt
stays accurate even if we add or remove workflows.

How ABI discovers this agent
-----------------------------
BaseModule.on_load() in Module.py calls ModuleAgentLoader.load_agents(),
which scans <module_root>/agents/*Agent.py and calls each class's New()
classmethod to construct the agent.  AbiAgent (the orchestrator) then
registers it as a sub-agent so it appears in the chat UI.
"""

from __future__ import annotations

from typing import Optional

from naas_abi_core.services.agent.Agent import (
    Agent,
    AgentConfiguration,
    AgentSharedState,
)


class DocsBotAgent(Agent):
    # We use the plain Agent base class rather than IntentAgent because
    # IntentAgent requires an embedding model for its intent-routing system.
    # DocsBot has no intent routing — it just calls SPARQL tools directly —
    # so the simpler base class is both correct and avoids the embedding dep.
    """Documentation knowledge-graph chat agent."""

    name: str = "DocsBot"
    description: str = (
        "Answers questions about the Kubernetes documentation using a structured "
        "knowledge graph.  Can find which procedures mention a term, analyse the "
        "impact of changing a definition, list topics by subject area, or surface "
        "orphaned pages."
    )
    avatar_url: str = ""  # optional: URL to a logo image shown in Naas chat UI

    # The [TOOLS] placeholder is replaced at construction time with a formatted
    # list of available tool names and descriptions (see New() below).
    system_prompt: str = """<role>
You are DocsBot, an AI assistant with direct access to a structured knowledge
graph of the Kubernetes documentation corpus.  You answer questions about doc
structure, terminology, and relationships with precision — citing specific page
titles and Confluence paths in every answer.
</role>

<ontology>
The knowledge graph uses these node types (RDF classes):
- ConceptTopic   — "what is X" explanatory pages
- TaskTopic      — step-by-step how-to procedures
- ReferenceTopic — lookup material, API specs
- GlossaryEntry  — definitions of single vocabulary terms
- SectionTopic   — container/index pages grouping child topics

Edges between nodes:
- docs:mentions   — a topic body uses a vocabulary term
- docs:defines    — a GlossaryEntry is the authoritative definition of a term
- docs:references — a hyperlink from one topic to another
- docs:partOf     — a topic belongs to a section (transitive)
- docs:hasSubject — a topic is tagged with a taxonomy subject

Every topic has:
- dcterms:title        — the page title
- docs:canonicalPath   — the path on the Kubernetes docs site (and in Confluence)
</ontology>

<tools>
[TOOLS]
</tools>

<operating_guidelines>
- Always call a tool before answering a question about doc content.
- Include the canonicalPath in every topic you mention so users can navigate directly.
- When reporting impact analysis, present the summary table first, then details.
- If a query returns zero results, say so clearly and suggest a spelling check on the term.
- Never invent topic titles or paths — only report what the graph returns.
</operating_guidelines>

<constraints>
- Do not answer from training-data knowledge about Kubernetes — use only graph results.
- If asked something the available tools cannot answer, say so and list what you can answer.
</constraints>
"""

    suggestions: list[dict] = [
        {
            "label": "Find tasks for a term",
            "value": "Which task topics mention the term 'statefulset'?",
            "description": "Find how-to procedures that reference a specific glossary term",
        },
        {
            "label": "Impact analysis",
            "value": "If we change the definition of 'pod', what's the blast radius?",
            "description": "See how many pages mention a term, grouped by type",
        },
        {
            "label": "Browse by subject",
            "value": "Show me all topics tagged with the 'storage' subject",
            "description": "Inventory topics by taxonomy subject area",
        },
        {
            "label": "Find orphan pages",
            "value": "Which concept topics have no inbound links?",
            "description": "Surface pages that aren't linked from anywhere",
        },
    ]

    @classmethod
    def New(
        cls,
        agent_shared_state: Optional[AgentSharedState] = None,
        agent_configuration: Optional[AgentConfiguration] = None,
    ) -> "DocsBotAgent":  # type: ignore[override]
        """Construct a fully-wired DocsBotAgent.

        ABI's module loader calls this classmethod.  We import the docsbot
        module instance here (inside the method) to avoid circular imports at
        module load time — the engine must finish loading before we can call
        get_instance().
        """
        from naas_abi_core.engine.context import get_default_model_registry

        # --- Get the chat and embedding models from ABI's model registry ----
        # The registry is populated by whichever AI provider modules are
        # enabled in config.yaml (e.g. naas_abi_marketplace.ai.chatgpt).
        registry = get_default_model_registry()
        assert registry is not None, (
            "ModelRegistryService not initialized. "
            "Make sure an AI provider module (e.g. ai.chatgpt) is enabled in config.yaml."
        )
        chat_model = registry.get_default_chat_model()
        # DocsBot only calls SPARQL tools — no vector search, no embedding needed.

        # --- Get the running module instance to access config + triple store -
        from docsbot import ABIModule
        module = ABIModule.get_instance()
        triple_store = module._engine.services.triple_store

        # --- Instantiate all four SPARQL workflow tools ----------------------
        from docsbot.workflows.FindTasksWorkflow import (
            FindTasksWorkflow,
            FindTasksWorkflowConfiguration,
        )
        from docsbot.workflows.ImpactAnalysisWorkflow import (
            ImpactAnalysisWorkflow,
            ImpactAnalysisWorkflowConfiguration,
        )
        from docsbot.workflows.TopicsBySubjectWorkflow import (
            TopicsBySubjectWorkflow,
            TopicsBySubjectWorkflowConfiguration,
        )
        from docsbot.workflows.OrphanTopicsWorkflow import (
            OrphanTopicsWorkflow,
            OrphanTopicsWorkflowConfiguration,
        )

        tools = []
        tools += FindTasksWorkflow(
            FindTasksWorkflowConfiguration(triple_store=triple_store)
        ).as_tools()
        tools += ImpactAnalysisWorkflow(
            ImpactAnalysisWorkflowConfiguration(triple_store=triple_store)
        ).as_tools()
        tools += TopicsBySubjectWorkflow(
            TopicsBySubjectWorkflowConfiguration(triple_store=triple_store)
        ).as_tools()
        tools += OrphanTopicsWorkflow(
            OrphanTopicsWorkflowConfiguration(triple_store=triple_store)
        ).as_tools()

        # --- Fill the [TOOLS] placeholder in the system prompt ---------------
        tools_list = "\n".join(
            f"- {tool.name}: {tool.description}" for tool in tools
        )
        system_prompt = cls.system_prompt.replace("[TOOLS]", tools_list)

        if agent_configuration is None:
            agent_configuration = AgentConfiguration(system_prompt=system_prompt)
        if agent_shared_state is None:
            agent_shared_state = AgentSharedState(thread_id="0")

        return cls(
            name=cls.name,
            description=cls.description,
            chat_model=chat_model,
            tools=tools,
            state=agent_shared_state,
            configuration=agent_configuration,
            memory=None,
        )
