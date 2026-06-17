---
id: ray-core.patterns.ray-get-submission-order
title: 'Anti-pattern: Processing results in submission order using ray.get increases
  runtime'
topic_type: concept
description: ''
subjects:
- core
mentions:
- task
references: []
canonical_path: /en/latest/ray-core/patterns/ray-get-submission-order
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/patterns/ray-get-submission-order.rst
license: Apache 2.0, The Ray Authors
---

Anti-pattern: Processing results in submission order using ray.get increases runtime

**TLDR:** Avoid processing independent results in submission order using ray.get() since results may be ready in a different order than the submission order.

A batch of tasks is submitted, and we need to process their results individually once they’re done.
If each task takes a different amount of time to finish and we process results in submission order, we may waste time waiting for all of the slower (straggler) tasks that were submitted earlier to finish while later faster tasks have already finished.

Instead, we want to process the tasks in the order that they finish using ray.wait() to speed up total time to completion.

    Processing results in submission order vs completion order

Code example

Other `ray.get()` related anti-patterns are:

- unnecessary-ray-get
- ray-get-loop
