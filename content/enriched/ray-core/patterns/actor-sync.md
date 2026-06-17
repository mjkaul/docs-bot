---
id: ray-core.patterns.actor-sync
title: 'Pattern: Using an actor to synchronize other tasks and actors'
topic_type: concept
description: ''
subjects:
- core
mentions:
- actor
- task
references: []
canonical_path: /en/latest/ray-core/patterns/actor-sync
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/patterns/actor-sync.rst
license: Apache 2.0, The Ray Authors
---

Pattern: Using an actor to synchronize other tasks and actors

When you have multiple tasks that need to wait on some condition or otherwise
need to synchronize across tasks & actors on a cluster, you can use a central
actor to coordinate among them.

Example use case

You can use an actor to implement a distributed `asyncio.Event` that multiple tasks can wait on.

Code example
