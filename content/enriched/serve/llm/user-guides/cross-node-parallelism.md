---
id: serve.llm.user-guides.cross-node-parallelism
title: Cross-node parallelism
topic_type: task
description: ''
subjects:
- serve
- core
mentions:
- actor
- deployment
- placement-group
- replica
- worker
references: []
canonical_path: /en/latest/serve/llm/user-guides/cross-node-parallelism
source: https://github.com/ray-project/ray/blob/master/doc/source/serve/llm/user-guides/cross-node-parallelism.md
license: Apache 2.0, The Ray Authors
---

# Cross-node parallelism

Ray Serve LLM supports cross-node tensor parallelism (TP) and pipeline parallelism (PP), which distribute model inference across multiple GPUs and nodes. Use cross-node parallelism to:

- Deploy models that don't fit on a single GPU or node.
- Scale model serving across your cluster's available resources.
- Use Ray's placement group strategies to control worker placement for performance or fault tolerance.

:
> **Note:** By default, Ray Serve LLM uses the `PACK` placement strategy, which tries to place workers on as few nodes as possible. If workers can't fit on a single node, they automatically spill to other nodes. This enables cross-node deployments when single-node resources are insufficient.
:

## Tensor parallelism

Tensor parallelism splits model weights across multiple GPUs, with each GPU processing a portion of the model's tensors for each forward pass. This approach is useful for models that don't fit on a single GPU.

The following example shows how to configure tensor parallelism across 2 GPUs:

::::{tab-set}

:::{tab-item} Python
:sync: python

[code example]
:::

::::

## Pipeline parallelism

Pipeline parallelism splits the model's layers across multiple GPUs, with each GPU processing a subset of the model's layers. This approach is useful for very large models where tensor parallelism alone isn't sufficient.

The following example shows how to configure pipeline parallelism across 2 GPUs:

::::{tab-set}

:::{tab-item} Python
:sync: python

[code example]
:::

::::

## Combined tensor and pipeline parallelism

For extremely large models, you can combine both tensor and pipeline parallelism. The total number of GPUs is the product of `tensor_parallel_size` and `pipeline_parallel_size`.

The following example shows how to configure a model with both TP and PP (4 GPUs total):

::::{tab-set}

:::{tab-item} Python
:sync: python

[code example]
:::

::::

## Custom placement groups

You can customize how Ray places vLLM engine workers across nodes using `placement_group_config` with either `bundle_per_worker` (simple) or `bundles` (advanced).

### Basic configuration with bundle_per_worker

Use the `bundle_per_worker` option inside `placement_group_config` to specify resources for each worker without manually creating the full bundle list. Ray automatically replicates this bundle based on `tensor_parallel_size * pipeline_parallel_size`. This field is mutually exclusive with `bundles`.

> **Note:** In each bundle dict, `CPU` and `GPU` are numeric amounts. If you omit either key, it is treated as **0** — set both explicitly when your workers need CPUs and GPUs (there is no implicit default GPU when you only specify CPU, or vice versa).

::::{tab-set}

:::{tab-item} Python
:sync: python

[code example]
:::

::::

### Advanced configuration with bundles

For full control over bundle specification and placement strategy, use `placement_group_config` with `bundles`. This accepts a dictionary with `bundles` (a list of resource dictionaries) and `strategy` (placement strategy).

Ray Serve LLM uses the `PACK` strategy by default, which tries to place workers on as few nodes as possible. If workers can't fit on a single node, they automatically spill to other nodes. For more details on all available placement strategies, see Ray Core's placement strategies documentation.

:
> **Note:** Data parallel deployments automatically override the placement strategy to `STRICT_PACK` because each replica must be co-located for correct data parallel behavior.
:

While you can specify the degree of tensor and pipeline parallelism, the specific assignment of model ranks to GPUs is managed by the vLLM engine and can't be directly configured through the Ray Serve LLM API. Ray Serve automatically injects accelerator type labels into bundles and merges the first bundle with replica actor resources (CPU, GPU, memory).

The following example shows how to use the `SPREAD` strategy to distribute workers across multiple nodes for fault tolerance:

::::{tab-set}

:::{tab-item} Python
:sync: python

[code example]
:::

::::
