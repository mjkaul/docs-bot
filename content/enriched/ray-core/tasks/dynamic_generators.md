---
id: ray-core.tasks.dynamic_generators
title: Dynamic generators
topic_type: concept
description: ''
subjects:
- core
mentions:
- actor
- object-ref
- object-store
- task
references: []
canonical_path: /en/latest/ray-core/tasks/dynamic_generators
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/tasks/dynamic_generators.rst
license: Apache 2.0, The Ray Authors
---

Dynamic generators

> **Warning:** `num_returns="dynamic"` generator API is soft deprecated as of Ray 2.8 due to its limitation.
Use the streaming generator API instead.

Python generators are functions that behave like iterators, yielding one
value per iteration. Ray supports remote generators for two use cases:

1. To reduce max heap memory usage when returning multiple values from a remote
   function. See the design pattern guide for an
   example.
2. When the number of return values is set dynamically by the remote function
   instead of by the caller.

Remote generators can be used in both actor and non-actor tasks.

`num_returns` set by the task caller

Where possible, the caller should set the remote function's number of return values using `@ray.remote(num_returns=x)` or `foo.options(num_returns=x).remote()`.
Ray will return this many `ObjectRefs` to the caller.
The remote task should then return the same number of values, usually as a tuple or list.
Compared to setting the number of return values dynamically, this adds less complexity to user code and less performance overhead, as Ray will know exactly how many `ObjectRefs` to return to the caller ahead of time.

Without changing the caller's syntax, we can also use a remote generator function to yield the values iteratively.
The generator should yield the same number of return values specified by the caller, and these will be stored one at a time in Ray's object store.
An error will be raised for generators that yield a different number of values from the one specified by the caller.

For example, we can swap the following code that returns a list of return values:

for this code, which uses a generator function:

The advantage of doing so is that the generator function does not need to hold all of its return values in memory at once.
It can yield the arrays one at a time to reduce memory pressure.

`num_returns` set by the task executor

In some cases, the caller may not know the number of return values to expect from a remote function.
For example, suppose we want to write a task that breaks up its argument into equal-size chunks and returns these.
We may not know the size of the argument until we execute the task, so we don't know the number of return values to expect.

In these cases, we can use a remote generator function that returns a *dynamic* number of values.
To use this feature, set `num_returns="dynamic"` in the `@ray.remote` decorator or the remote function's `.options()`.
Then, when invoking the remote function, Ray will return a *single* `ObjectRef` that will get populated with an `DynamicObjectRefGenerator` when the task completes.
The `DynamicObjectRefGenerator` can be used to iterate over a list of `ObjectRefs` containing the actual values returned by the task.

We can also pass the `ObjectRef` returned by a task with `num_returns="dynamic"` to another task. The task will receive the `DynamicObjectRefGenerator`, which it can use to iterate over the task's return values. Similarly, you can also pass an `ObjectRefGenerator` as a task argument.

Exception handling

If a generator function raises an exception before yielding all its values, the values that it already stored will still be accessible through their `ObjectRefs`.
The remaining `ObjectRefs` will contain the raised exception.
This is true for both static and dynamic `num_returns`.
If the task was called with `num_returns="dynamic"`, the exception will be stored as an additional final `ObjectRef` in the `DynamicObjectRefGenerator`.

Note that there is currently a known bug where exceptions will not be propagated for generators that yield more values than expected. This can occur in two cases:

1. When `num_returns` is set by the caller, but the generator task returns more than this value.
2. When a generator task with `num_returns="dynamic"` is re-executed, and the re-executed task yields more values than the original execution. Note that in general, Ray does not guarantee correctness for task re-execution if the task is nondeterministic, and it is recommended to set `@ray.remote(max_retries=0)` for such tasks.

Limitations

Although a generator function creates `ObjectRefs` one at a time, currently Ray will not schedule dependent tasks until the entire task is complete and all values have been created. This is similar to the semantics used by tasks that return multiple values as a list.
