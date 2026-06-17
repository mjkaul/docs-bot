---
id: serve.llm.architecture.serving-patterns.index
title: Serving patterns
topic_type: section
description: ''
subjects:
- serve
mentions:
- deployment
- replica
references: []
canonical_path: /en/latest/serve/llm/architecture/serving-patterns/index
source: https://github.com/ray-project/ray/blob/master/doc/source/serve/llm/architecture/serving-patterns/index.md
license: Apache 2.0, The Ray Authors
---

# Serving patterns

Architecture documentation for distributed LLM serving patterns.

[code example]

## Overview

Ray Serve LLM supports several serving patterns that can be combined for complex deployment scenarios:

- Data parallel attention: scale throughput by running multiple coordinated engine replicas that process requests in parallel, replicating attention while sharding requests across the replicas.
- Prefill-decode disaggregation: optimize resource utilization by separating prompt processing from token generation.

These patterns are composable and can be mixed to meet specific requirements for throughput, latency, and cost optimization.

These pages describe how each pattern works. For step-by-step configuration, see the matching how-to guides: Data parallel attention and Prefill/decode disaggregation.
