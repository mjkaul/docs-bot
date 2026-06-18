import Anthropic from "@anthropic-ai/sdk";
import { NextRequest } from "next/server";
import { getStore } from "@/lib/graph";
import {
  findTasksForTerm,
  impactOfTerm,
  topicsBySubject,
  orphanTopics,
} from "@/lib/sparql";

const MODEL = "claude-sonnet-4-5";

const SYSTEM_PROMPT = `You are DocsBot, an assistant that answers questions about Ray documentation \
using a structured knowledge graph built from the official Ray docs (ray-project/ray, Apache 2.0).

The graph covers: Ray Core, Ray Serve, Ray Train, Ray Tune, Ray Data, and Ray Observability. \
Taxonomy subjects are: core, serve, train, tune, data, observability, cluster.

When the user asks about documentation topics, terms, or subject areas, use your tools to query \
the graph and ground every claim in real data. Always cite specific page titles and canonical paths \
from tool results. If a tool returns no results, say so — do not guess or hallucinate content.`;

const TOOLS: Anthropic.Tool[] = [
  {
    name: "find_tasks_for_term",
    description:
      "Find all task (how-to) topics in the Ray documentation that mention a specific glossary term. " +
      "Use for questions like 'Which how-to pages cover Actors?' or 'What tasks mention deployments?'",
    input_schema: {
      type: "object" as const,
      properties: {
        term_id: {
          type: "string",
          description:
            "Glossary term slug — lowercase, hyphen-separated. " +
            "Examples: 'actor', 'deployment', 'remote-function', 'dataset', 'trial', 'trainer'.",
        },
      },
      required: ["term_id"],
    },
  },
  {
    name: "impact_of_term",
    description:
      "Analyse the blast radius of changing a vocabulary term: returns a count of how many " +
      "documentation topics (grouped by type) mention it, plus an optional list of titles. " +
      "Use before renaming or redefining a term, or to answer 'How widely used is X?'",
    input_schema: {
      type: "object" as const,
      properties: {
        term_id: {
          type: "string",
          description: "Glossary term slug, e.g. 'actor', 'deployment', 'dataset'.",
        },
        include_titles: {
          type: "boolean",
          description: "If true (default), return individual topic titles alongside counts.",
        },
      },
      required: ["term_id"],
    },
  },
  {
    name: "topics_by_subject",
    description:
      "List all documentation topics tagged with a taxonomy subject: " +
      "'core', 'serve', 'train', 'tune', 'data', 'observability', or 'cluster'. " +
      "Optionally filter to a specific topic type. " +
      "Use for questions like 'Show me all Ray Train concept pages' or 'What tasks cover Ray Serve?'",
    input_schema: {
      type: "object" as const,
      properties: {
        subject_id: {
          type: "string",
          description:
            "Taxonomy subject slug. Valid values: 'core', 'serve', 'train', 'tune', 'data', 'observability', 'cluster'.",
        },
        topic_type: {
          type: "string",
          description:
            "Optional filter. One of: 'ConceptTopic', 'TaskTopic', 'ReferenceTopic', 'GlossaryEntry', 'SectionTopic'.",
        },
      },
      required: ["subject_id"],
    },
  },
  {
    name: "orphan_topics",
    description:
      "Find documentation topics that no other topic links to — topics with no inbound references. " +
      "Useful for identifying content gaps or isolated pages.",
    input_schema: {
      type: "object" as const,
      properties: {
        topic_type: {
          type: "string",
          description: "Topic class to check: 'ConceptTopic' (default), 'TaskTopic', 'ReferenceTopic'.",
        },
        limit: {
          type: "number",
          description: "Maximum number of results. Default: 50.",
        },
      },
      required: [],
    },
  },
];

async function dispatchTool(
  name: string,
  input: Record<string, unknown>
): Promise<string> {
  const store = getStore();
  try {
    let result: unknown;
    if (name === "find_tasks_for_term") {
      result = await findTasksForTerm(store, input.term_id as string);
    } else if (name === "impact_of_term") {
      result = await impactOfTerm(
        store,
        input.term_id as string,
        input.include_titles !== false
      );
    } else if (name === "topics_by_subject") {
      result = await topicsBySubject(
        store,
        input.subject_id as string,
        input.topic_type as string | undefined
      );
    } else if (name === "orphan_topics") {
      result = await orphanTopics(
        store,
        (input.topic_type as string) ?? "ConceptTopic",
        (input.limit as number) ?? 50
      );
    } else {
      result = { error: `Unknown tool: ${name}` };
    }
    return JSON.stringify(result);
  } catch (err) {
    return JSON.stringify({ error: String(err) });
  }
}

export async function POST(req: NextRequest) {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return new Response(JSON.stringify({ error: "ANTHROPIC_API_KEY not set" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }

  const { messages } = await req.json();

  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      function send(event: string, data: unknown) {
        controller.enqueue(
          encoder.encode(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`)
        );
      }

      try {
        const client = new Anthropic({ apiKey });
        const history: Anthropic.MessageParam[] = [...messages];

        while (true) {
          const response = await client.messages.create({
            model: MODEL,
            max_tokens: 4096,
            system: SYSTEM_PROMPT,
            tools: TOOLS,
            messages: history,
          });

          history.push({ role: "assistant", content: response.content });

          if (response.stop_reason === "end_turn") {
            for (const block of response.content) {
              if (block.type === "text") {
                send("text", { text: block.text });
              }
            }
            break;
          }

          if (response.stop_reason === "tool_use") {
            const toolResults: Anthropic.ToolResultBlockParam[] = [];
            for (const block of response.content) {
              if (block.type === "tool_use") {
                send("tool_call", { name: block.name, input: block.input });
                const result = await dispatchTool(
                  block.name,
                  block.input as Record<string, unknown>
                );
                toolResults.push({
                  type: "tool_result",
                  tool_use_id: block.id,
                  content: result,
                });
              }
            }
            history.push({ role: "user", content: toolResults });
          } else {
            for (const block of response.content) {
              if (block.type === "text") send("text", { text: block.text });
            }
            break;
          }
        }
      } catch (err) {
        send("error", { message: String(err) });
      } finally {
        send("done", {});
        controller.close();
      }
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}
