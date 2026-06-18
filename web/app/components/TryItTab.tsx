"use client";

import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const SUGGESTED_QUERIES = [
  "Which task topics mention the term actor?",
  "What is the blast radius of changing the term deployment?",
  "Show me all Ray Train task topics",
  "Which concept topics have no inbound links?",
  "Compare Ray Serve and Ray Data: how many topics does each have?",
  "What are the top 3 most widely referenced glossary terms?",
];

interface ToolCall {
  name: string;
  input: Record<string, unknown>;
}

interface Message {
  role: "user" | "assistant";
  text: string;
  toolCalls?: ToolCall[];
}

export default function TryItTab() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function submit(question: string) {
    if (!question.trim() || loading) return;
    const userMsg: Message = { role: "user", text: question };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    const apiMessages = [
      ...messages.map((m) => ({ role: m.role, content: m.text })),
      { role: "user", content: question },
    ];

    const assistantMsg: Message = { role: "assistant", text: "", toolCalls: [] };
    setMessages((prev) => [...prev, assistantMsg]);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: apiMessages }),
      });

      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buf = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });

        const parts = buf.split("\n\n");
        buf = parts.pop() ?? "";

        for (const part of parts) {
          const eventLine = part.split("\n").find((l) => l.startsWith("event:"));
          const dataLine = part.split("\n").find((l) => l.startsWith("data:"));
          if (!eventLine || !dataLine) continue;

          const event = eventLine.replace("event: ", "").trim();
          const data = JSON.parse(dataLine.replace("data: ", "").trim());

          if (event === "tool_call") {
            setMessages((prev) => {
              const next = [...prev];
              const last = { ...next[next.length - 1] };
              last.toolCalls = [...(last.toolCalls ?? []), data as ToolCall];
              next[next.length - 1] = last;
              return next;
            });
          } else if (event === "text") {
            setMessages((prev) => {
              const next = [...prev];
              const last = { ...next[next.length - 1] };
              last.text = data.text;
              next[next.length - 1] = last;
              return next;
            });
          }
        }
      }
    } catch (err) {
      setMessages((prev) => {
        const next = [...prev];
        const last = { ...next[next.length - 1] };
        last.text = `Error: ${String(err)}`;
        next[next.length - 1] = last;
        return next;
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Suggested queries — only show when empty */}
      {messages.length === 0 && (
        <div className="flex-1 flex flex-col items-center justify-center px-6 py-12">
          <div className="max-w-xl w-full">
            <p className="text-xs font-semibold tracking-widest text-indigo-600 uppercase mb-3 text-center">
              Knowledge graph
            </p>
            <h2 className="text-2xl font-bold text-gray-900 text-center mb-2">
              Ask about the Ray docs
            </h2>
            <p className="text-sm text-gray-500 text-center mb-8">
              Every answer is grounded in the knowledge graph — no hallucination, just facts.
            </p>
            <div className="grid grid-cols-1 gap-2">
              {SUGGESTED_QUERIES.map((q) => (
                <button
                  key={q}
                  onClick={() => submit(q)}
                  className="text-left px-4 py-3 rounded-lg border border-gray-200 bg-white text-sm text-gray-700 hover:border-indigo-300 hover:bg-indigo-50 hover:text-indigo-700 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Message thread */}
      {messages.length > 0 && (
        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6 max-w-3xl mx-auto w-full">
          {messages.map((msg, i) => (
            <div key={i}>
              {msg.role === "user" ? (
                <div className="flex justify-end">
                  <div className="max-w-lg bg-indigo-600 text-white rounded-2xl rounded-tr-sm px-4 py-3 text-sm">
                    {msg.text}
                  </div>
                </div>
              ) : (
                <div className="flex gap-3">
                  <div className="w-7 h-7 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <div className="flex-1 min-w-0">
                    {/* Tool call traces */}
                    {msg.toolCalls && msg.toolCalls.length > 0 && (
                      <div className="mb-3 space-y-1">
                        {msg.toolCalls.map((tc, j) => (
                          <div
                            key={j}
                            className="text-xs font-mono text-gray-400 bg-gray-50 rounded px-3 py-1.5 border border-gray-100"
                          >
                            <span className="text-indigo-400 mr-1">→</span>
                            <span className="text-gray-500">{tc.name}</span>
                            <span className="text-gray-400">
                              ({JSON.stringify(tc.input)})
                            </span>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Loading spinner */}
                    {loading && i === messages.length - 1 && !msg.text && (
                      <div className="flex items-center gap-2 text-sm text-gray-400">
                        <div className="w-3 h-3 border border-indigo-400 border-t-transparent rounded-full animate-spin" />
                        Querying graph…
                      </div>
                    )}

                    {/* Answer */}
                    {msg.text && (
                      <div className="prose text-sm text-gray-700">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {msg.text}
                        </ReactMarkdown>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
      )}

      {/* Input */}
      <div className="border-t border-gray-200 bg-white px-4 py-4">
        <div className="max-w-3xl mx-auto flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && submit(input)}
            placeholder="Ask about the Ray knowledge graph…"
            disabled={loading}
            className="flex-1 border border-gray-200 rounded-lg px-4 py-2.5 text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:opacity-50"
          />
          <button
            onClick={() => submit(input)}
            disabled={loading || !input.trim()}
            className="px-4 py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-40 transition-colors"
          >
            Ask
          </button>
        </div>
        {messages.length > 0 && (
          <div className="max-w-3xl mx-auto mt-2 flex flex-wrap gap-2">
            {SUGGESTED_QUERIES.slice(0, 3).map((q) => (
              <button
                key={q}
                onClick={() => submit(q)}
                disabled={loading}
                className="text-xs text-gray-400 hover:text-indigo-600 transition-colors disabled:opacity-40 truncate max-w-xs"
              >
                {q}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
