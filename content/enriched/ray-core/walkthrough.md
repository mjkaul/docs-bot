---
id: ray-core.walkthrough
title: What's Ray Core?
topic_type: concept
description: ''
subjects:
- core
mentions:
- actor
- object-ref
- object-store
- task
- worker
references: []
canonical_path: /en/latest/ray-core/walkthrough
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/walkthrough.rst
license: Apache 2.0, The Ray Authors
---

What's Ray Core?

    Key Concepts <key-concepts>
    User Guides <user-guide>
    Examples <examples/overview>
    api/index
    Internals <internals>

Ray Core is a powerful distributed computing framework that provides a small set of essential primitives (tasks, actors, and objects) for building and scaling distributed applications.
This walk-through introduces you to these core concepts with simple examples that demonstrate how to transform your Python functions and classes into distributed Ray tasks and actors, and how to work effectively with Ray objects.

> **Note:** Ray has introduced an experimental API to transfer objects using GLOO / NCCL / NIXL / (bring your own)
as an alternative to the default shared memory + gRPC based object store.
See Ray Direct Transport for more details.

Getting Started

To get started, install Ray using `pip install -U ray`. For additional installation options, see Installing Ray.

The first step is to import and initialize Ray:

> **Note:** Unless you explicitly call `ray.init()`, the first use of a Ray remote API call will implicitly call `ray.init()` with no arguments.

Running a Task

Tasks are the simplest way to parallelize your Python functions across a Ray cluster. To create a task:

1. Decorate your function with `@ray.remote` to indicate it should run remotely
2. Call the function with `.remote()` instead of a normal function call
3. Use `ray.get()` to retrieve the result from the returned future (Ray *object reference*)

Here's a simple example:

Calling an Actor

While tasks are stateless, Ray actors allow you to create stateful workers that maintain their internal state between method calls.
When you instantiate a Ray actor:

1. Ray starts a dedicated worker process somewhere in your cluster
2. The actor's methods run on that specific worker and can access and modify its state
3. The actor executes method calls serially in the order it receives them, preserving consistency

Here's a simple Counter example:

The preceding example demonstrates basic actor usage. For a more comprehensive example that combines both tasks and actors, see the Monte Carlo Pi estimation example.

Passing Objects

Ray's distributed object store efficiently manages data across your cluster. There are three main ways to work with objects in Ray:

1. **Implicit creation**: When tasks and actors return values, they are automatically stored in Ray's distributed object store, returning *object references* that can be later retrieved.
2. **Explicit creation**: Use `ray.put()` to directly place objects in the store.
3. **Passing references**: You can pass object references to other tasks and actors, avoiding unnecessary data copying and enabling lazy execution.

Here's an example showing these techniques:

Next Steps

You can combine Ray's simple primitives in powerful ways to express virtually any distributed computation pattern. To dive deeper into Ray's key concepts,
explore these user guides:

    :gutter: 1
    :class-container: container pb-3

    .. grid-item-card::
        :img-top: /images/tasks.png
        :class-img-top: pt-2 w-75 d-block mx-auto fixed-height-img

        .. button-ref:: ray-remote-functions

            Using remote functions (Tasks)

    .. grid-item-card::
        :img-top: /images/actors.png
        :class-img-top: pt-2 w-75 d-block mx-auto fixed-height-img

        .. button-ref:: ray-remote-classes

            Using remote classes (Actors)

    .. grid-item-card::
        :img-top: /images/objects.png
        :class-img-top: pt-2 w-75 d-block mx-auto fixed-height-img

        .. button-ref:: objects-in-ray

            Working with Ray Objects
