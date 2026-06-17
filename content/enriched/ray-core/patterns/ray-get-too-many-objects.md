---
id: ray-core.patterns.ray-get-too-many-objects
title: 'Anti-pattern: Fetching too many objects at once with ray.get causes failure'
topic_type: concept
description: ''
subjects:
- core
mentions:
- object-store
- task
references: []
canonical_path: /en/latest/ray-core/patterns/ray-get-too-many-objects
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/patterns/ray-get-too-many-objects.rst
license: Apache 2.0, The Ray Authors
---

Anti-pattern: Fetching too many objects at once with ray.get causes failure

**TLDR:** Avoid calling ray.get() on too many objects since this will lead to heap out-of-memory or object store out-of-space. Instead fetch and process one batch at a time.

If you have a large number of tasks that you want to run in parallel, trying to do `ray.get()` on all of them at once could lead to failure with heap out-of-memory or object store out-of-space since Ray needs to fetch all the objects to the caller at the same time.
Instead you should get and process the results one batch at a time. Once a batch is processed, Ray will evict objects in that batch to make space for future batches.

    Fetching too many objects at once with `ray.get()`

Code example

**Anti-pattern:**

**Better approach:**

Here besides getting one batch at a time to avoid failure, we are also using `ray.wait()` to process results in the finish order instead of the submission order to reduce the runtime. See ray-get-submission-order for more details.
