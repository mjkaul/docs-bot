---
id: ray-core.patterns.return-ray-put
title: 'Anti-pattern: Returning ray.put() ObjectRefs from a task harms performance
  and fault tolerance'
topic_type: concept
description: ''
subjects:
- core
mentions:
- driver
- object-ref
- object-store
- task
- worker
references: []
canonical_path: /en/latest/ray-core/patterns/return-ray-put
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/patterns/return-ray-put.rst
license: Apache 2.0, The Ray Authors
---

Anti-pattern: Returning ray.put() ObjectRefs from a task harms performance and fault tolerance

**TLDR:** Avoid calling ray.put() on task return values and returning the resulting ObjectRefs.
Instead, return these values directly if possible.

Returning ray.put() ObjectRefs are considered anti-patterns for the following reasons:

- It disallows inlining small return values: Ray has a performance optimization to return small (<= 100KB) values inline directly to the caller, avoiding going through the distributed object store.
  On the other hand, `ray.put()` will unconditionally store the value to the object store which makes the optimization for small return values impossible.
- Returning ObjectRefs involves extra distributed reference counting protocol which is slower than returning the values directly.
- It's less fault tolerant: the worker process that calls `ray.put()` is the "owner" of the returned `ObjectRef` and the return value fate shares with the owner. If the worker process dies, the return value is lost.
  In contrast, the caller process (often the driver) is the owner of the return value if it's returned directly.

Code example

If you want to return a single value regardless if it's small or large, you should return it directly.

If you want to return multiple values and you know the number of returns before calling the task, you should use the num_returns option.

If you don't know the number of returns before calling the task, you should use the dynamic generator pattern if possible.
