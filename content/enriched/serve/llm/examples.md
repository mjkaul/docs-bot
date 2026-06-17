---
id: serve.llm.examples
title: Examples
topic_type: concept
description: ''
subjects:
- serve
mentions:
- deployment
references: []
canonical_path: /en/latest/serve/llm/examples
source: https://github.com/ray-project/ray/blob/master/doc/source/serve/llm/examples.md
license: Apache 2.0, The Ray Authors
---

# Examples

End-to-end tutorials for deploying LLMs with Ray Serve. Each one walks through configuration, deployment, and querying for a representative model. For the minimal path, start with the Quickstart.

## By model size

- Deploy a small-sized LLM: serve a model that fits on a single GPU. The best starting point.
- Deploy a medium-sized LLM: shard a model across multiple GPUs on one node with tensor parallelism.
- Deploy a large-sized LLM: span a model across multiple nodes with cross-node parallelism.

## By capability

- Deploy a vision LLM: serve a vision-language model that accepts image inputs.
- Deploy a reasoning LLM: serve a reasoning model and handle its reasoning output.
- Deploy a hybrid reasoning LLM: serve a model that can switch reasoning on and off per request.
- Deploy gpt-oss: deploy OpenAI's open-weight gpt-oss model.

[code example]
