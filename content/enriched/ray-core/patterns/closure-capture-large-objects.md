---
id: ray-core.patterns.closure-capture-large-objects
title: 'Anti-pattern: Closure capturing large objects harms performance'
topic_type: concept
description: ''
subjects:
- core
mentions:
- object-store
- task
references: []
canonical_path: /en/latest/ray-core/patterns/closure-capture-large-objects
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/patterns/closure-capture-large-objects.rst
license: Apache 2.0, The Ray Authors
---

Anti-pattern: Closure capturing large objects harms performance

**TLDR:** Avoid closure capturing large objects in remote functions or classes, use object store instead.

When you define a ray.remote function or class,
it is easy to accidentally capture large (more than a few MB) objects implicitly in the definition.
This can lead to slow performance or even OOM since Ray is not designed to handle serialized functions or classes that are very large.

For such large objects, there are two options to resolve this problem:

- Use ray.put() to put the large objects in the Ray object store, and then pass object references as arguments to the remote functions or classes (*"better approach #1"* below)
- Create the large objects inside the remote functions or classes by passing a lambda method (*"better approach #2"*). This is also the only option for using unserializable objects.

Code example

**Anti-pattern:**

**Better approach #1:**

**Better approach #2:**
