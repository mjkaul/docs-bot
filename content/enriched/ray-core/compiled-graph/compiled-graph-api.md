---
id: ray-core.compiled-graph.compiled-graph-api
title: Compiled Graph API
topic_type: concept
description: ''
subjects:
- core
mentions:
- actor
- compiled-graph
references: []
canonical_path: /en/latest/ray-core/compiled-graph/compiled-graph-api
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/compiled-graph/compiled-graph-api.rst
license: Apache 2.0, The Ray Authors
---

Compiled Graph API

Input and Output Nodes

    ray.dag.input_node.InputNode
    ray.dag.output_node.MultiOutputNode

DAG Construction

    ray.actor.ActorMethod.bind
    ray.dag.DAGNode.with_tensor_transport
    ray.experimental.compiled_dag_ref.CompiledDAGRef

Compiled Graph Operations

    ray.dag.DAGNode.experimental_compile
    ray.dag.compiled_dag_node.CompiledDAG.execute
    ray.dag.compiled_dag_node.CompiledDAG.visualize

Configurations

    ray.dag.context.DAGContext
