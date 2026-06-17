---
id: ray-core.patterns.tree-of-actors
title: 'Pattern: Using a supervisor actor to manage a tree of actors'
topic_type: concept
description: ''
subjects:
- core
mentions:
- actor
- driver
- task
- worker
references: []
canonical_path: /en/latest/ray-core/patterns/tree-of-actors
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/patterns/tree-of-actors.rst
license: Apache 2.0, The Ray Authors
---

Pattern: Using a supervisor actor to manage a tree of actors

Actor supervision is a pattern in which a supervising actor manages a collection of worker actors.
The supervisor delegates tasks to subordinates and handles their failures.
This pattern simplifies the driver since it manages only a few supervisors and does not deal with failures from worker actors directly.
Furthermore, multiple supervisors can act in parallel to parallelize more work.

    Tree of actors

> **Note:** - If the supervisor dies (or the driver), the worker actors are automatically terminated thanks to actor reference counting.
- Actors can be nested to multiple levels to form a tree.

Example use case

You want to do data parallel training and train the same model with different hyperparameters in parallel.
For each hyperparameter, you can launch a supervisor actor to do the orchestration and it will create worker actors to do the actual training per data shard.

> **Note:** For data parallel training and hyperparameter tuning, it's recommended to use Ray Train (~ray.train.data_parallel_trainer.DataParallelTrainer and Ray Tune's Tuner)
which applies this pattern under the hood.

Code example
