---
id: ray-core.fault_tolerance.nodes
title: Node Fault Tolerance
topic_type: concept
description: ''
subjects:
- core
mentions:
- actor
- head-node
- task
- worker
references: []
canonical_path: /en/latest/ray-core/fault_tolerance/nodes
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/fault_tolerance/nodes.rst
license: Apache 2.0, The Ray Authors
---

Node Fault Tolerance

A Ray cluster consists of one or more worker nodes,
each of which consists of worker processes and system processes (e.g. raylet).
One of the worker nodes is designated as the head node and has extra processes like the GCS.

Here, we describe node failures and their impact on tasks, actors, and objects.

Worker node failure

When a worker node fails, all the running tasks and actors will fail and all the objects owned by worker processes of this node will be lost. In this case, the tasks, actors, objects fault tolerance mechanisms will kick in and try to recover the failures using other worker nodes.

Head node failure

When a head node fails, the entire Ray cluster fails.
To tolerate head node failures, we need to make GCS fault tolerant
so that when we start a new head node we still have all the cluster-level data.

Raylet failure

When a raylet process fails, the corresponding node will be marked as dead and is treated the same as a node failure.
Each raylet is associated with a unique id, so even if the raylet restarts on the same physical machine,
it'll be treated as a new raylet/node to the Ray cluster.
