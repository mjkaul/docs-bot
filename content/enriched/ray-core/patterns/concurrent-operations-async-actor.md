---
id: ray-core.patterns.concurrent-operations-async-actor
title: 'Pattern: Using asyncio to run actor methods concurrently'
topic_type: concept
description: ''
subjects:
- core
mentions:
- actor
- object-ref
- task
references: []
canonical_path: /en/latest/ray-core/patterns/concurrent-operations-async-actor
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/patterns/concurrent-operations-async-actor.rst
license: Apache 2.0, The Ray Authors
---

Pattern: Using asyncio to run actor methods concurrently

By default, a Ray actor runs in a single thread and
actor method calls are executed sequentially. This means that a long running method call blocks all the following ones.
In this pattern, we use `await` to yield control from the long running method call so other method calls can run concurrently.
Normally the control is yielded when the method is doing IO operations but you can also use `await asyncio.sleep(0)` to yield control explicitly.

> **Note:** You can also use threaded actors to achieve concurrency.

Example use case

You have an actor with a long polling method that continuously fetches tasks from the remote store and executes them.
You also want to query the number of tasks executed while the long polling method is running.

With the default actor, the code will look like this:

This is problematic because `TaskExecutor.run` method runs forever and never yields control to run other methods.
We can solve this problem by using async actors and use `await` to yield control:

Here, instead of using the blocking ray.get() to get the value of an ObjectRef, we use `await` so it can yield control while we are waiting for the object to be fetched.
