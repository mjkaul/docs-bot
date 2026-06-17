---
id: ray-core.patterns.index
title: Design Patterns & Anti-patterns
topic_type: section
description: ''
subjects:
- core
mentions:
- actor
- task
references: []
canonical_path: /en/latest/ray-core/patterns/index
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/patterns/index.rst
license: Apache 2.0, The Ray Authors
---

Design Patterns & Anti-patterns

This section is a collection of common design patterns and anti-patterns for writing Ray applications.

    nested-tasks
    generators
    limit-pending-tasks
    limit-running-tasks
    concurrent-operations-async-actor
    actor-sync
    tree-of-actors
    pipelining
    return-ray-put
    nested-ray-get
    ray-get-loop
    unnecessary-ray-get
    ray-get-submission-order
    ray-get-too-many-objects
    too-fine-grained-tasks
    redefine-task-actor-loop
    pass-large-arg-by-value
    closure-capture-large-objects
    global-variables
    out-of-band-object-ref-serialization
    fork-new-processes
