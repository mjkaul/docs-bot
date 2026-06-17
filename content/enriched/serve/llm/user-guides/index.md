---
id: serve.llm.user-guides.index
title: User guides
topic_type: section
description: ''
subjects:
- serve
- core
mentions:
- deployment
- placement-group
- replica
references: []
canonical_path: /en/latest/serve/llm/user-guides/index
source: https://github.com/ray-project/ray/blob/master/doc/source/serve/llm/user-guides/index.md
license: Apache 2.0, The Ray Authors
---

# User guides

How-to guides for deploying, scaling, and operating Ray Serve LLM. If you are new, start with the Quickstart, then come back here to go deeper.

## Configure and deploy

- Configuration reference: every `LLMConfig` field, from model loading and engine kwargs to accelerators, placement, and deployment options.
- Deployment initialization: speed up model loading and replica startup with caching, streaming load formats, and initialization callbacks.
- Multi-LoRA deployment: serve many LoRA adapters on a shared base model with runtime switching and an LRU cache.

## Scale across GPUs and nodes

- Cross-node parallelism: distribute a model across GPUs and nodes with tensor and pipeline parallelism and placement groups.
- Data parallel attention: replicate the model into coordinated data-parallel groups to raise throughput, especially for MoE models.
- Fractional GPU serving: pack multiple small-model replicas onto a single GPU.

## Optimize latency and throughput

- Prefill/decode disaggregation: split prompt processing and token generation onto separate replicas to tune each independently.
- KV cache offloading: extend KV cache capacity with LMCache and tiered storage backends.
- Prefix-aware routing: route requests to replicas that already hold a matching prefix to maximize cache hits.
- Direct streaming: bypass the ingress when streaming tokens to cut per-token latency.

## Choose an engine

- vLLM compatibility: use vLLM features such as embeddings, structured outputs, vision, and reasoning through Ray Serve LLM.
- SGLang integration: run SGLang as the inference engine instead of vLLM.

## Operate in production

- Observability and monitoring: engine and request metrics, Grafana dashboards, and Prometheus integration.

[code example]
