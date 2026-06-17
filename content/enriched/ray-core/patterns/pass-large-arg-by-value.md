---
id: ray-core.patterns.pass-large-arg-by-value
title: 'Anti-pattern: Passing the same large argument by value repeatedly harms performance'
topic_type: concept
description: ''
subjects:
- core
mentions:
- object-ref
- object-store
- task
- worker
references: []
canonical_path: /en/latest/ray-core/patterns/pass-large-arg-by-value
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/patterns/pass-large-arg-by-value.rst
license: Apache 2.0, The Ray Authors
---

Anti-pattern: Passing the same large argument by value repeatedly harms performance

**TLDR:** Avoid passing the same large argument by value to multiple tasks, use ray.put() and pass by reference instead.

When passing a large argument (>100KB) by value to a task,
Ray will implicitly store the argument in the object store and the worker process will fetch the argument to the local object store from the caller's object store before running the task.
If we pass the same large argument to multiple tasks, Ray will end up storing multiple copies of the argument in the object store since Ray doesn't do deduplication.

Instead of passing the large argument by value to multiple tasks,
we should use `ray.put()` to store the argument to the object store once and get an `ObjectRef`,
then pass the argument reference to tasks. This way, we make sure all tasks use the same copy of the argument, which is faster and uses less object store memory.

Code example

**Anti-pattern:**

**Better approach:**
