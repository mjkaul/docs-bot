"use client";

import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { SectionTree, PageMeta } from "@/lib/pageTree";

const TOPIC_TYPE_BADGE: Record<string, { label: string; color: string }> = {
  concept: { label: "Concept", color: "bg-blue-100 text-blue-700" },
  task: { label: "Task", color: "bg-green-100 text-green-700" },
  reference: { label: "Reference", color: "bg-purple-100 text-purple-700" },
  glossary: { label: "Glossary", color: "bg-amber-100 text-amber-700" },
};

interface DocContent {
  meta: PageMeta;
  body: string;
}

export default function DocsTab({ tree }: { tree: SectionTree[] }) {
  const [expanded, setExpanded] = useState<Set<string>>(
    () => new Set(tree.map((s) => s.section))
  );
  const [selected, setSelected] = useState<PageMeta | null>(
    tree[0]?.pages[0] ?? null
  );
  const [content, setContent] = useState<DocContent | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selected) return;
    setLoading(true);
    fetch(`/api/doc?path=${encodeURIComponent(selected.path)}`)
      .then((r) => r.json())
      .then((data) => {
        setContent(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [selected]);

  function toggleSection(section: string) {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(section)) next.delete(section);
      else next.add(section);
      return next;
    });
  }

  const badge = content
    ? TOPIC_TYPE_BADGE[content.meta.topic_type] ?? TOPIC_TYPE_BADGE["concept"]
    : null;

  return (
    <div className="flex h-full overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 flex-shrink-0 border-r border-gray-200 bg-gray-50 overflow-y-auto">
        <div className="px-3 py-4">
          {tree.map((section) => (
            <div key={section.section} className="mb-2">
              {/* Section header */}
              <button
                onClick={() => toggleSection(section.section)}
                className="w-full flex items-center justify-between px-2 py-1.5 rounded text-xs font-semibold text-gray-500 uppercase tracking-wider hover:bg-gray-100 transition-colors"
              >
                <span>{section.label}</span>
                <svg
                  className={`w-3 h-3 transition-transform ${
                    expanded.has(section.section) ? "rotate-90" : ""
                  }`}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </button>

              {/* Pages */}
              {expanded.has(section.section) && (
                <div className="mt-1 space-y-0.5">
                  {section.pages.map((page) => (
                    <button
                      key={page.id}
                      onClick={() => setSelected(page)}
                      className={`w-full text-left px-3 py-1.5 rounded text-sm transition-colors truncate ${
                        selected?.id === page.id
                          ? "bg-indigo-50 text-indigo-700 font-medium"
                          : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                      }`}
                      title={page.title}
                    >
                      {page.title}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </aside>

      {/* Content pane */}
      <main className="flex-1 overflow-y-auto">
        {loading && (
          <div className="flex items-center justify-center h-48">
            <div className="w-5 h-5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {!loading && content && (
          <article className="max-w-3xl mx-auto px-8 py-8">
            {/* Page header */}
            <div className="mb-6 pb-4 border-b border-gray-100">
              <div className="flex items-center gap-2 mb-2">
                {badge && (
                  <span
                    className={`text-xs font-medium px-2 py-0.5 rounded-full ${badge.color}`}
                  >
                    {badge.label}
                  </span>
                )}
                <span className="text-xs text-gray-400 font-mono">
                  {content.meta.id}
                </span>
              </div>
              <h1 className="text-2xl font-bold text-gray-900">
                {content.meta.title}
              </h1>
            </div>

            {/* Body */}
            <div className="prose text-gray-700 text-sm">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {content.body}
              </ReactMarkdown>
            </div>
          </article>
        )}

        {!loading && !content && selected && (
          <div className="flex items-center justify-center h-48 text-sm text-gray-400">
            Failed to load page.
          </div>
        )}

        {!loading && !selected && (
          <div className="flex items-center justify-center h-48 text-sm text-gray-400">
            Select a page from the sidebar.
          </div>
        )}
      </main>
    </div>
  );
}
