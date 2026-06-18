const STEPS = [
  {
    number: "01",
    title: "Content as files",
    body: "Every topic is a plain Markdown or RST file in a folder. No proprietary format, no lock-in. Files are versioned, diffed, and processed by scripts — the same discipline applied to code.",
    detail: "274 Ray docs files · Apache 2.0",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
  },
  {
    number: "02",
    title: "Typed topics",
    body: "Each file is classified as a concept (what something is), task (how to do it), reference (lookup material), or glossary term. Information typing is the highest-leverage metadata in the system.",
    detail: "ConceptTopic · TaskTopic · ReferenceTopic · GlossaryEntry",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
      </svg>
    ),
  },
  {
    number: "03",
    title: "Controlled vocabulary",
    body: "A shared glossary is the spine of the system. Every time a topic mentions a defined term, that connection is recorded — not inferred by a model. The graph grows from editorial discipline.",
    detail: "28 Ray terms · actor · deployment · dataset · trial · trainer…",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
      </svg>
    ),
  },
  {
    number: "04",
    title: "Knowledge graph",
    body: "Types, terms, mentions, and cross-references compile into an RDF graph. Every relationship is explicit, inspectable, and queryable with SPARQL. Think of it as a map where every road is a documented link.",
    detail: "3,283 triples · OWL ontology · Turtle serialization",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
  },
  {
    number: "05",
    title: "AI agent",
    body: "Claude queries the graph with SPARQL tools. Facts come from the database — deterministic, citable, never hallucinated. The language model's job shrinks to what it's actually good at: understanding questions and phrasing answers.",
    detail: "Claude claude-sonnet-4-5 · 4 tools · tool-use loop",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
      </svg>
    ),
  },
];

const STATS = [
  { value: "274", label: "source files" },
  { value: "3,283", label: "graph triples" },
  { value: "28", label: "glossary terms" },
  { value: "4", label: "SPARQL tools" },
];

export default function HowItWorks() {
  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      {/* Intro */}
      <div className="mb-12">
        <p className="text-xs font-semibold tracking-widest text-indigo-600 uppercase mb-3">
          Framework
        </p>
        <h2 className="text-3xl font-bold text-gray-900 mb-4 leading-tight">
          Your structure becomes<br />the AI&rsquo;s brain.
        </h2>
        <p className="text-lg text-gray-500 max-w-2xl leading-relaxed">
          Most &ldquo;chat with your docs&rdquo; tools chop content into arbitrary chunks and fuzzy-match against questions. This system takes the opposite approach — make the structure explicit, and let the AI navigate facts instead of guessing from text.
        </p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-4 gap-4 mb-12">
        {STATS.map((stat) => (
          <div key={stat.label} className="bg-gray-50 rounded-lg px-4 py-4 text-center">
            <div className="text-2xl font-bold text-indigo-600 mb-1">{stat.value}</div>
            <div className="text-xs text-gray-500 font-medium">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Pipeline steps */}
      <div className="relative">
        {/* Connector line */}
        <div className="absolute left-[1.85rem] top-10 bottom-10 w-px bg-gray-200 hidden md:block" />

        <div className="space-y-6">
          {STEPS.map((step, i) => (
            <div key={step.number} className="relative flex gap-6 group">
              {/* Step indicator */}
              <div className="flex-shrink-0 w-14 flex flex-col items-center">
                <div className="w-10 h-10 rounded-full bg-indigo-600 text-white flex items-center justify-center z-10 relative shadow-sm group-hover:bg-indigo-700 transition-colors">
                  {step.icon}
                </div>
              </div>

              {/* Content card */}
              <div className="flex-1 bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:shadow-md hover:border-indigo-100 transition-all mb-1">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <span className="text-xs font-semibold text-indigo-400 font-mono mr-2">
                      {step.number}
                    </span>
                    <span className="text-base font-semibold text-gray-900">
                      {step.title}
                    </span>
                  </div>
                </div>
                <p className="text-sm text-gray-600 leading-relaxed mb-3">
                  {step.body}
                </p>
                <p className="text-xs text-gray-400 font-mono">{step.detail}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Why this matters */}
      <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          {
            title: "Deterministic answers",
            body: "\"Which topics mention this term?\" has one correct answer. The graph returns it — no hallucination possible.",
          },
          {
            title: "Impact analysis",
            body: "Before renaming a term: one query shows every page that mentions it, grouped by type. Content strategy, not guesswork.",
          },
          {
            title: "Fully inspectable",
            body: "When the AI cites a relationship, you can open the graph file and find the exact triple. Compare that to a vector database.",
          },
        ].map((item) => (
          <div key={item.title} className="bg-indigo-50 rounded-xl p-5 border border-indigo-100">
            <h3 className="text-sm font-semibold text-indigo-900 mb-2">{item.title}</h3>
            <p className="text-sm text-indigo-700 leading-relaxed">{item.body}</p>
          </div>
        ))}
      </div>

      {/* Footer credit */}
      <div className="mt-12 pt-8 border-t border-gray-100 text-center">
        <p className="text-sm text-gray-400">
          Framework based on{" "}
          <a
            href="https://www.linkedin.com/in/michael-iantosca/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-600 font-medium hover:text-indigo-600 transition-colors"
          >
            Michael Iantosca&rsquo;s
          </a>{" "}
          enterprise content engineering approach. Built by{" "}
          <span className="text-gray-600 font-medium">Matthew Kaul</span> in
          collaboration with{" "}
          <a
            href="https://claude.ai"
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-600 font-medium hover:text-indigo-600 transition-colors"
          >
            Claude
          </a>
          .
        </p>
      </div>
    </div>
  );
}
