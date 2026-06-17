---
id: ray-core.direct-transport.custom-tensor-transport
title: Implementing a custom tensor transport (Advanced)
topic_type: concept
description: ''
subjects:
- core
mentions:
- actor
- driver
- object-ref
- task
references: []
canonical_path: /en/latest/ray-core/direct-transport/custom-tensor-transport
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/direct-transport/custom-tensor-transport.rst
license: Apache 2.0, The Ray Authors
---

Implementing a custom tensor transport (Advanced)

Ray Direct Transport (RDT) allows you to register custom tensor transports at runtime.
This page explains how to implement a custom tensor transport by implementing the TensorTransportManager abstract interface.

Overview

To create a custom tensor transport:

1. Implement the abstract interface ray.experimental.TensorTransportManager.
2. Define custom metadata classes by extending TensorTransportMetadata and CommunicatorMetadata.
3. Register your transport using ray.experimental.register_tensor_transport.

When Ray needs to transfer a tensor between actors using your transport, it calls specific methods on your `TensorTransportManager` implementation at different stages of the transfer lifecycle.

Implementing TensorTransportManager

The TensorTransportManager abstract class defines the interface for custom tensor transports. You must implement all abstract methods.

The following diagram shows when each method is called during a tensor transfer:

   Source Actor                    Owner Process                 Destination Actor
   ============                    =============                 =================
        |                               |                               |
   1. Task returns tensor               |                               |
      `extract_tensor_transport_metadata`                             |
        |                               |                               |
        | ---- transport_metadata ----> |                               |
        |                               |                               |
        |                     2. Prepare communicator                   |
        |                        `get_communicator_metadata`          |
        |                               |                               |
        | <---- comm metadata --------- | ---- comm metadata -------->  |
        |                               |                               |
   3. `send_multiple_tensors`         |          3. `recv_multiple_tensors`
                                        |                               |
        | ------------ tensors ---------------------------------------> |
        |                               |                               |
        |                         (transfer complete)                   |
        |                               |                               |
        |                      5. Ref goes out of scope                 |
        | <---------------------------- |                               |
   5. Clean up resources                |                               |
      `garbage_collect`               |                               |

Note that Ray will not call `send_multiple_tensors` for one-sided transports.
The following diagram shows where each method is called in the ray.put / ray.get case supported by one-sided transports.

   Source Actor                                                  Destination Actor
   ============                                                  =================
        |                                                               |
   1. User `ray.put`'s tensor                                         |
      `extract_tensor_transport_metadata`                             |
        |                                                               |
        |                                                               |
   2. User passes ref to another actor                                  |
        | ---- transport_metadata ---------------------------------->   |
        |                                                               |
        |                                                               |
        |                                          3. User `ray.get`'s on object ref
                                                      `get_communicator_metadata`
        |                                              `recv_multiple_tensors`
        | ------------ tensors --------- -----------------------------> |
        |                                                               |
        |                         (transfer complete)                   |
        |                                                               |
   4. Clean up resources                                                |
      `garbage_collect`                                               |
   (when ref goes out of scope)                                         |

The API reference page for TensorTransportManager has more details on what each method does and how to implement them.
See implementations of Ray's default transports (NCCL, NIXL, etc.) in the [python/ray/experimental/rdt/](https://github.com/ray-project/ray/tree/master/python/ray/experimental/rdt) directory.
The following is an walk-through for implementing and using a custom tensor transport.

Example: Shared memory tensor transport

The following walks through a complete custom tensor transport that transfers `numpy` arrays through shared memory.

Note that because shared memory is one-sided (the receiver directly reads the memory block the sender wrote to),
`is_one_sided` returns `True` and Ray never calls `send_multiple_tensors`.

Define metadata classes

Your transport uses two metadata classes that flow through different stages of the transfer:

- TensorTransportMetadata is created on the **source actor** during `extract_tensor_transport_metadata`. It carries per-tensor information (shapes, dtypes, devices) plus any transport-specific identifiers (e.g., shared memory block names, RDMA keys) that the receiver needs to locate and read the data.

- CommunicatorMetadata is created on the **owner/driver process** during `get_communicator_metadata`. It carries any coordination information both actors need, such as ranks in a collective group. For one-sided transports (where the receiver can directly read the sender's memory), an empty metadata object is typically sufficient.

Start by extending these classes to carry any transport-specific state.
`ShmTransportMetadata` stores the shared memory block name and size so the receiver can locate and read the data.
This transport doesn't need any communicator metadata, so `ShmCommunicatorMetadata` is empty.

Extract tensor transport metadata

Ray calls `extract_tensor_transport_metadata` on the source actor right after the task produces its result tensors.
Record shapes and dtypes, then perform any transport-specific registration. Here, the implementation serializes the tensors
into a shared memory block and records the block name and size in the metadata so the receiver can find it.

Get communicator metadata

Ray calls `get_communicator_metadata` on the owner/driver process before orchestrating the transfer.
Return any information both actors need to coordinate, such as ranks in a collective group.
For one-sided transports such as shared memory, an empty metadata object is fine.

Transport properties

Define your `TensorTransportManager` subclass and implement the property methods.
`tensor_transport_backend` returns the name that users pass to `@ray.method(tensor_transport=...)`.
`is_one_sided` and `can_abort_transport` tell Ray how to orchestrate transfers and handle errors.
`actor_has_tensor_transport` lets Ray check whether a given actor can use this transport.

Send and receive

`recv_multiple_tensors` runs on the destination actor. For this shared memory transport, it opens the
shared memory block by name and deserializes the tensors.

`send_multiple_tensors` runs on the source actor for two-sided transports. Since shared memory is one-sided,
Ray never calls this method, so it raises `NotImplementedError` as a safety guard.

Cleanup

`garbage_collect` runs on the source actor when Ray's reference counting determines the object is out of scope.
Release any transport resources here, in this case closing and unlinking the shared memory block.

`abort_transport` runs on both actors when a system error occurs during transfer, if `can_abort_transport` returns `True`.
Since this transport returns `False` for `can_abort_transport`, Ray kills the involved actors instead,
so `abort_transport` is a no-op.

Registering your transport

After implementing your transport, the **driver process** must register it with ray.experimental.register_tensor_transport before creating any actors that use it:

Limitations

Custom tensor transports have the following limitations:

- **Actor restarts aren't supported.** Your actor doesn't have access to the custom transport after a restart.

- **Register transports before actor creation.** If you register a transport after creating an actor, that actor can't use the new transport.

- **Out-of-order actors** If you have an out-of-order actor (such as an async actor) and the process where you submit the actor task is different from where you created the actor, Ray can't guarantee it has registered your custom transport on the actor at task execution time.

- **Actor creation and task submission from different processes** If the process where you submit an actor task is different from where you created the actor, Ray can't guarantee it has registered your custom transport on the actor at task execution time.

For general RDT limitations, see limitations.

Also feel free to reach out through [GitHub issues](https://github.com/ray-project/ray/issues) or the [Ray Slack](https://docs.google.com/forms/d/e/1FAIpQLSfAcoiLCHOguOm8e7Jnn-JJdZaCxPGjgVCvFijHB5PLaQLeig/viewform) to ask any questions.
