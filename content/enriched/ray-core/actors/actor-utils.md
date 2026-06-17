---
id: ray-core.actors.actor-utils
title: Utility Classes
topic_type: concept
description: ''
subjects:
- core
mentions:
- actor
- task
references: []
canonical_path: /en/latest/ray-core/actors/actor-utils
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/actors/actor-utils.rst
license: Apache 2.0, The Ray Authors
---

Utility Classes

Actor Pool

        The `ray.util` module contains a utility class, `ActorPool`.
        This class is similar to multiprocessing.Pool and lets you schedule Ray tasks over a fixed pool of actors.

        
        See the package reference for more information.

    
        Actor pool hasn't been implemented in Java yet.

    
        Actor pool hasn't been implemented in C++ yet.

Message passing using Ray Queue

Sometimes just using one signal to synchronize is not enough. If you need to send data among many tasks or
actors, you can use ray.util.queue.Queue.

Ray's Queue API has a similar API to Python's `asyncio.Queue` and `queue.Queue`.
