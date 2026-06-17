---
id: serve.llm.architecture.index
title: Architecture
topic_type: section
description: ''
subjects:
- serve
mentions:
- deployment
- replica
references: []
canonical_path: /en/latest/serve/llm/architecture/index
source: https://github.com/ray-project/ray/blob/master/doc/source/serve/llm/architecture/index.md
license: Apache 2.0, The Ray Authors
---

# Architecture

How Ray Serve LLM is built: the components a deployment is made of, how a request flows through them, and the patterns that scale serving across GPUs and nodes. Read these to extend the system or to reason about performance. To deploy models, see the User guides instead.

Start with the overview, then read the pages relevant to your use case:

- Architecture overview: the components of a deployment (engine, server, ingress) and how a request flows through them. Read this first.
- Core components: the key abstractions and extension points, including the engine protocol, `LLMConfig`, the builder functions, and custom server classes.
- Serving patterns: distributed patterns (data parallel attention, prefill-decode disaggregation) and how they compose.
- Request routing: how a replica is selected for each request, the built-in policies, and how to write a custom router.

[code example]
