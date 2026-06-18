# DocsBot Front-End — Shaping Doc

**Selected shape:** D (Three-tab wiki + chat)  
**Stack:** Next.js on Vercel

---

## Requirements (R)

| ID | Requirement | Status |
|----|-------------|--------|
| R0 | A visitor opens a link and can understand the framework, browse the docs, and query the live AI agent — in one place, no setup | Core goal |
| R1 | No login, no install — works immediately from a URL | Must-have |
| R2 | Framework explanation is visual and concise — peer-level tone for experienced tech writers | Must-have |
| R3 | Live chat queries Claude against the Ray docs knowledge graph (Anthropic API proxied server-side) | Must-have |
| R4 | The page communicates that this was built by you, in collaboration with Claude | Must-have |
| R5 | Free hosting with a server component (API key never exposed to client) | Must-have |
| R6 | Visually compelling — portfolio-quality, not a developer demo | Must-have |
| R7 | A "Docs" tab presents enriched Ray content as browsable, Confluence-style wiki pages with left sidebar page tree | Must-have |
| R8 | "Try it" tab includes clickable suggested queries to lower friction for non-technical visitors | Must-have |

---

## Shape D: Three-tab wiki + chat

| Part | Mechanism | Flag |
|------|-----------|:----:|
| D1 | Tab shell — three tabs: "How it works," "Docs," "Try it" | |
| D2 | "How it works" tab — visual pipeline overview: 5 steps as designed cards | |
| D3 | "Docs" tab — left sidebar page tree (sections: Core, Serve, Train, Tune, Data, Observability), right pane renders enriched markdown | |
| D4 | "Try it" tab — chat interface; shows tool calls as they fire | |
| D5 | Server-side `/api/chat` Next.js route proxies Anthropic calls; API key never reaches client | |
| D6 | Built-by attribution — visible on the page, names author and Claude | |

---

## Fit Check (R × D)

| Req | Requirement | Status | D |
|-----|-------------|--------|---|
| R0 | A visitor opens a link and can understand the framework, browse the docs, and query the live AI agent — in one place, no setup | Core goal | ✅ |
| R1 | No login, no install — works immediately from a URL | Must-have | ✅ |
| R2 | Framework explanation is visual and concise — peer-level tone for experienced tech writers | Must-have | ✅ |
| R3 | Live chat queries Claude against the Ray docs knowledge graph (Anthropic API proxied server-side) | Must-have | ✅ |
| R4 | The page communicates that this was built by you, in collaboration with Claude | Must-have | ✅ |
| R5 | Free hosting with a server component (API key never exposed to client) | Must-have | ✅ |
| R6 | Visually compelling — portfolio-quality, not a developer demo | Must-have | ✅ |
| R7 | A "Docs" tab presents enriched Ray content as browsable, Confluence-style wiki pages with left sidebar page tree | Must-have | ✅ |
| R8 | "Try it" tab includes clickable suggested queries to lower friction for non-technical visitors | Must-have | ✅ |

---

## Detail D: Breadboard

### UI Affordances

| ID | Affordance | Place |
|----|-----------|-------|
| U1 | Tab bar — "How it works / Docs / Try it" | Browser |
| U2 | Pipeline steps — 5-step visual cards | Browser |
| U3 | Attribution block — "Built by [name] with Claude" | Browser |
| U4 | Page tree sidebar — sections + nested pages, expandable | Browser |
| U5 | Doc content pane — rendered markdown | Browser |
| U6 | Suggested query chips — clickable pre-written questions | Browser |
| U7 | Chat input + send button | Browser |
| U8 | Chat message thread — user and assistant turns | Browser |
| U9 | Tool call trace — inline `→ tool_name(args)` as calls fire | Browser |

### Non-UI Affordances

| ID | Affordance | Place |
|----|-----------|-------|
| N1 | Page tree manifest — directory walk of `content/enriched/` at build time → JSON | Next.js build |
| N2 | Markdown renderer — `react-markdown` + `remark-gfm` | Browser |
| N3 | `/api/chat` route — receives messages, runs Claude tool-use loop, streams SSE | Next.js server |
| N4 | Tool dispatcher — routes `tool_use` blocks to SPARQL functions | Next.js server |
| N5 | Graph + SPARQL — Turtle file loaded at server startup; queries via `comunica` + `n3.js` (JS port of `agent/sparql.py`) | Next.js server |
| N6 | Suggested queries — static array of pre-written questions | Browser |

---

## Slices

### V1 — Shell + "How it works" tab

Scaffold Next.js app, wire Vercel deployment, build framework explanation tab. No backend.

| ID | Affordance |
|----|-----------|
| U1 | Tab bar (only "How it works" active; others placeholder) |
| U2 | Pipeline steps — 5-step visual cards |
| U3 | Attribution block |

**Demo:** Open the Vercel URL and see a polished framework overview.

---

### V2 — "Docs" tab

Build-time manifest + sidebar + markdown rendering. Still no API.

| ID | Affordance |
|----|-----------|
| N1 | Page tree manifest built from `content/enriched/` |
| U4 | Page tree sidebar, sections expandable |
| N2 | Markdown renderer |
| U5 | Doc content pane |

**Demo:** Click "Docs," browse Ray Core → Actors, see the enriched page render cleanly.

---

### V3 — "Try it" tab + live AI

Chat UI wired to Claude with full tool-use loop and graph queries.

| ID | Affordance |
|----|-----------|
| N6 | Suggested queries — static list |
| U6 | Suggested query chips |
| U7 | Chat input + send |
| N3 | `/api/chat` route with Claude tool-use loop |
| N4 | Tool dispatcher |
| N5 | Graph loaded from `docs_graph.ttl`; SPARQL via `comunica` + `n3.js` |
| U8 | Message thread |
| U9 | Tool call trace |

**Demo:** Click a suggested query, watch tool calls fire in real time, read a grounded answer citing real Ray doc pages.
