---
id: ray-core.patterns.limit-pending-tasks
title: 'Pattern: Using ray.wait to limit the number of pending tasks'
topic_type: concept
description: ''
subjects:
- core
mentions:
- actor
- task
- worker
references: []
canonical_path: /en/latest/ray-core/patterns/limit-pending-tasks
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/patterns/limit-pending-tasks.rst
license: Apache 2.0, The Ray Authors
---

Pattern: Using ray.wait to limit the number of pending tasks

In this pattern, we use ray.wait() to limit the number of pending tasks.

If we continuously submit tasks faster than their process time, we will accumulate tasks in the pending task queue, which can eventually cause OOM.
With `ray.wait()`, we can apply backpressure and limit the number of pending tasks so that the pending task queue won't grow indefinitely and cause OOM.

> **Note:** If we submit a finite number of tasks, it's unlikely that we will hit the issue mentioned above since each task only uses a small amount of memory for bookkeeping in the queue.
It's more likely to happen when we have an infinite stream of tasks to run.

> **Note:** This method is meant primarily to limit how many tasks should be in flight at the same time.
It can also be used to limit how many tasks can run *concurrently*, but it is not recommended, as it can hurt scheduling performance.
Ray automatically decides task parallelism based on resource availability, so the recommended method for adjusting how many tasks can run concurrently is to modify each task's resource requirements instead.

Example use case

You have a worker actor that processes tasks at a rate of X tasks per second and you want to submit tasks to it at a rate lower than X to avoid OOM.

For example, Ray Serve uses this pattern to limit the number of pending queries for each worker.

    Limit number of pending tasks

Code example

**Without backpressure:**

**With backpressure:**
