---
id: serve.llm.index
title: Serving LLMs
topic_type: section
description: ''
subjects:
- serve
mentions:
- deployment
references: []
canonical_path: /en/latest/serve/llm/index
source: https://github.com/ray-project/ray/blob/master/doc/source/serve/llm/index.md
license: Apache 2.0, The Ray Authors
---

# Serving LLMs

Ray Serve LLM deploys large language models in production. It builds on Ray Serve primitives for distributed, multi-node LLM serving and exposes an OpenAI-compatible API.

## Key features

- OpenAI-compatible API for chat, completions, and embeddings.
- Multi-node, multi-model deployment with autoscaling and load balancing.
- Parallelism strategies: tensor, pipeline, expert, and data parallel attention.
- Prefill-decode disaggregation to scale the prefill and decode phases independently.
- Custom request routing, including prefix-aware routing for higher cache hit rates.
- Multi-LoRA serving on a shared base model.
- Engine-agnostic backends such as vLLM and SGLang.
- Built-in metrics and Grafana dashboards.

## Install

Ray Serve LLM ships with Ray. Install it with the `llm` extra:

```bash
pip install "ray[llm]"
```

This pulls in vLLM and the OpenAI-compatible server stack. You need a GPU to run most models. The Quickstart covers prerequisites, supported hardware, and gated-model setup.

## Deploy your first model

Define an ~ray.serve.llm.LLMConfig, build an OpenAI-compatible app, and run it:

[code example]

Once it is running, query it with any OpenAI client at `http://localhost:8000/v1`. See the Quickstart for client snippets, multi-model apps, and config-driven (YAML) deployments.

## Find your path

- **New here?** Start with the Quickstart to deploy and query a model.
- **Configuring a deployment?** The Configuration reference explains every `LLMConfig` field.
- **Scaling up?** The User guides cover parallelism, routing, caching, LoRA, and observability.
- **Want the internals?** The Architecture docs explain components, request flow, and serving patterns.
- **Deploying a specific model?** The Examples walk through small, medium, large, vision, and reasoning models end to end.
- **Hitting an issue?** Check Troubleshooting and Benchmarks.

[code example]
