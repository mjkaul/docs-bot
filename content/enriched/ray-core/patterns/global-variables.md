---
id: ray-core.patterns.global-variables
title: 'Anti-pattern: Using global variables to share state between tasks and actors'
topic_type: concept
description: ''
subjects:
- core
mentions:
- actor
- task
references: []
canonical_path: /en/latest/ray-core/patterns/global-variables
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/patterns/global-variables.rst
license: Apache 2.0, The Ray Authors
---

Anti-pattern: Using global variables to share state between tasks and actors

**TLDR:** Don't use global variables to share state with tasks and actors. Instead, encapsulate the global variables in an actor and pass the actor handle to other tasks and actors.

Ray drivers, tasks and actors are running in
different processes, so they don’t share the same address space.
This means that if you modify global variables
in one process, changes are not reflected in other processes.

The solution is to use an actor's instance variables to hold the global state and pass the actor handle to places where the state needs to be modified or accessed.
Note that using class variables to manage state between instances of the same class is not supported.
Each actor instance is instantiated in its own process, so each actor will have its own copy of the class variables.

Code example

**Anti-pattern:**

**Better approach:**
