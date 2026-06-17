---
id: ray-core.fault-tolerance
title: Fault tolerance
topic_type: concept
description: ''
subjects:
- core
mentions:
- actor
- driver
- object-ref
- object-store
- task
- worker
references: []
canonical_path: /en/latest/ray-core/fault-tolerance
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/fault-tolerance.rst
license: Apache 2.0, The Ray Authors
---

Fault tolerance

Ray is a distributed system, and that means failures can happen. Generally, Ray classifies
failures into two classes:
1. application-level failures
2. system-level failures
Bugs in user-level code or external system failures trigger application-level failures.
Node failures, network failures, or just bugs in Ray trigger system-level failures.
The following section contains the mechanisms that Ray provides to allow applications to recover from failures.

To handle application-level failures, Ray provides mechanisms to catch errors,
retry failed code, and handle misbehaving code. See the pages for task and actor fault
tolerance for more information on these mechanisms.

Ray also provides several mechanisms to automatically recover from internal system-level failures like node failures.
In particular, Ray can automatically recover from some failures in the distributed object store.

How to write fault tolerant Ray applications

There are several recommendations to make Ray applications fault tolerant:

First, if the fault tolerance mechanisms provided by Ray don't work for you,
you can always catch exceptions caused by failures and recover manually.

Second, avoid letting an `ObjectRef` outlive its owner task or actor
(the task or actor that creates the initial `ObjectRef` by calling ray.put() or `foo.remote()`).
As long as there are still references to an object,
the owner worker of the object keeps running even after the corresponding task or actor finishes.
If the owner worker fails, Ray cannot recover the object automatically for those who try to access the object.
One example of creating such outlived objects is returning `ObjectRef` created by `ray.put()` from a task:

In the preceding example, object `x` outlives its owner task `a`.
If the worker process running task `a` fails, calling `ray.get` on `x_ref` afterwards results in an `OwnerDiedError` exception.

The following example is a fault tolerant version which returns `x` directly. In this example, the driver owns `x` and you only access it within the lifetime of the driver.
If `x` is lost, Ray can automatically recover it via lineage reconstruction.
See /ray-core/patterns/return-ray-put for more details.

Third, avoid using custom resource requirements that only particular nodes can satisfy.
If that particular node fails, Ray won't retry the running tasks or actors.

If you prefer running a task on a particular node, you can use the NodeAffinitySchedulingStrategy.
It allows you to specify the affinity as a soft constraint so even if the target node fails, the task can still be retried on other nodes.

More about Ray fault tolerance

    fault_tolerance/tasks.rst
    fault_tolerance/actors.rst
    fault_tolerance/objects.rst
    fault_tolerance/nodes.rst
    fault_tolerance/gcs.rst
