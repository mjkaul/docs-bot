---
id: ray-core.patterns.nested-ray-get
title: 'Anti-pattern: Calling ray.get on task arguments harms performance'
topic_type: concept
description: ''
subjects:
- core
mentions:
- object-ref
- task
references: []
canonical_path: /en/latest/ray-core/patterns/nested-ray-get
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/patterns/nested-ray-get.rst
license: Apache 2.0, The Ray Authors
---

Anti-pattern: Calling ray.get on task arguments harms performance

**TLDR:** If possible, pass `ObjectRefs` as direct task arguments, instead of passing a list as the task argument and then calling ray.get() inside the task.

When a task calls `ray.get()`, it must block until the value of the `ObjectRef` is ready.
If all cores are already occupied, this situation can lead to a deadlock, as the task that produces the `ObjectRef`'s value may need the caller task's resources in order to run.
To handle this issue, if the caller task would block in `ray.get()`, Ray temporarily releases the caller's CPU resources to allow the pending task to run.
This behavior can harm performance and stability because the caller continues to use a process and memory to hold its stack while other tasks run.

Therefore, it is always better to pass `ObjectRefs` as direct arguments to a task and avoid calling `ray.get` inside of the task, if possible.

For example, in the following code, prefer the latter method of invoking the dependent task.

Avoiding `ray.get` in nested tasks may not always be possible. Some valid reasons to call `ray.get` include:

- nested-tasks
- If the nested task has multiple `ObjectRefs` to `ray.get`, and it wants to choose the order and number to get.
