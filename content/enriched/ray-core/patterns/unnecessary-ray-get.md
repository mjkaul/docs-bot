---
id: ray-core.patterns.unnecessary-ray-get
title: 'Anti-pattern: Calling ray.get unnecessarily harms performance'
topic_type: concept
description: ''
subjects:
- core
mentions:
- driver
- task
- worker
references: []
canonical_path: /en/latest/ray-core/patterns/unnecessary-ray-get
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/patterns/unnecessary-ray-get.rst
license: Apache 2.0, The Ray Authors
---

Anti-pattern: Calling ray.get unnecessarily harms performance

**TLDR:** Avoid calling ray.get() unnecessarily for intermediate steps. Work with object references directly, and only call `ray.get()` at the end to get the final result.

When `ray.get()` is called, objects must be transferred to the worker/node that calls `ray.get()`. If you don't need to manipulate the object, you probably don't need to call `ray.get()` on it!

Typically, it’s best practice to wait as long as possible before calling `ray.get()`, or even design your program to avoid having to call `ray.get()` at all.

Code example

**Anti-pattern:**

**Better approach:**

Notice in the anti-pattern example, we call `ray.get()` which forces us to transfer the large rollout to the driver, then again to the *reduce* worker.

In the fixed version, we only pass the reference to the object to the *reduce* task.
The `reduce` worker will implicitly call `ray.get()` to fetch the actual rollout data directly from the `generate_rollout` worker, avoiding the extra copy to the driver.

Other `ray.get()` related anti-patterns are:

- ray-get-loop
- ray-get-submission-order
