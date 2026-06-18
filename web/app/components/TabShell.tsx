"use client";

import { useState } from "react";
import HowItWorks from "./HowItWorks";

const TABS = [
  { id: "how", label: "How it works" },
  { id: "docs", label: "Docs" },
  { id: "try", label: "Try it" },
] as const;

type TabId = (typeof TABS)[number]["id"];

export default function TabShell() {
  const [active, setActive] = useState<TabId>("how");

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white px-6 py-4 flex items-center justify-between flex-shrink-0">
        <div>
          <h1 className="text-lg font-semibold text-gray-900 tracking-tight">
            DocsBot
          </h1>
          <p className="text-xs text-gray-500 mt-0.5">
            Docs-as-code + knowledge graph · Ray documentation corpus
          </p>
        </div>
        <div className="text-xs text-gray-400 text-right">
          <span>Built by </span>
          <span className="font-medium text-gray-600">Matthew Kaul</span>
          <span className="text-gray-300 mx-1.5">·</span>
          <span>in collaboration with </span>
          <span className="font-medium text-gray-600">Claude</span>
        </div>
      </header>

      {/* Tab bar */}
      <nav className="border-b border-gray-200 bg-white px-6 flex-shrink-0">
        <div className="flex gap-0">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActive(tab.id)}
              className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                active === tab.id
                  ? "border-indigo-600 text-indigo-600"
                  : "border-transparent text-gray-500 hover:text-gray-800 hover:border-gray-300"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Content */}
      <main className="flex-1 overflow-auto">
        {active === "how" && <HowItWorks />}
        {active === "docs" && <ComingSoon label="Docs" description="Browse the Ray documentation corpus as a structured wiki — with a Confluence-style page tree." />}
        {active === "try" && <ComingSoon label="Try it" description="Query the knowledge graph live through Claude." />}
      </main>
    </div>
  );
}

function ComingSoon({ label, description }: { label: string; description: string }) {
  return (
    <div className="flex items-center justify-center h-full min-h-96">
      <div className="text-center max-w-sm">
        <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
          <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
        </div>
        <h3 className="text-sm font-medium text-gray-700 mb-1">{label}</h3>
        <p className="text-sm text-gray-400">{description}</p>
      </div>
    </div>
  );
}
