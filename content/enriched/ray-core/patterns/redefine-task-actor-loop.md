---
id: ray-core.patterns.redefine-task-actor-loop
title: 'Anti-pattern: Redefining the same remote function or class harms performance'
topic_type: concept
description: ''
subjects:
- core
mentions:
- actor
- task
- worker
references: []
canonical_path: /en/latest/ray-core/patterns/redefine-task-actor-loop
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/patterns/redefine-task-actor-loop.rst
license: Apache 2.0, The Ray Authors
---

Anti-pattern: Redefining the same remote function or class harms performance

**TLDR:** Avoid redefining the same remote function or class.

Decorating the same function or class multiple times using the ray.remote decorator leads to slow performance in Ray.
For each Ray remote function or class, Ray will pickle it and upload to GCS.
Later on, the worker that runs the task or actor will download and unpickle it.
Each decoration of the same function or class generates a new remote function or class from Ray's perspective.
As a result, the pickle, upload, download and unpickle work will happen every time we redefine and run the remote function or class.

Code example

**Anti-pattern:**

**Better approach:**

We should define the same remote function or class outside of the loop instead of multiple times inside a loop so that it's pickled and uploaded only once.
