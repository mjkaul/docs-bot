---
id: ray-core.compiled-graph.quickstart
title: Quickstart
topic_type: task
description: ''
subjects:
- core
mentions:
- actor
- compiled-graph
- driver
- object-store
- task
references: []
canonical_path: /en/latest/ray-core/compiled-graph/quickstart
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/compiled-graph/quickstart.rst
license: Apache 2.0, The Ray Authors
---

Quickstart

Hello World

This "hello world" example uses Ray Compiled Graph. First, install Ray.

    pip install "ray[cgraph]"
    
    # For a ray version before 2.41, use the following instead:
    # pip install "ray[adag]"

First, define a simple actor that echoes its argument.

Next instantiate the actor and use the classic Ray Core APIs `remote` and `ray.get` to execute tasks on the actor.

  Execution takes 969.0364822745323 us

Now, create an equivalent program using Ray Compiled Graph. 
First, define a graph to execute using classic Ray Core, without any compilation.
Later, compile this graph, to apply optimizations and prevent further modifications to the graph.

First, create a Ray DAG (directed acyclic graph), which is a lazily executed graph of Ray tasks.
Note 3 key differences with the classic Ray Core APIs:

1. Use the ray.dag.InputNode context manager to indicate which inputs to the DAG should be provided at run time.
2. Use bind() instead of remote() to indicate lazily executed Ray tasks.
3. Use execute() to execute the DAG.

Here, define a graph and execute it.
Note that there is **no** compilation happening here. This uses the same execution backend as the preceding example:

Next, compile the `dag` using the experimental_compile API.
The graph uses the same APIs for execution:

  Execution takes 86.72196418046951 us

The performance of the same task graph improved by 10X. This is because the function `echo` is cheap and thus highly affected by
the system overhead. Due to various bookkeeping and distributed protocols, the classic Ray Core APIs usually have 1 ms+ system overhead.

Because the system knows the task graph ahead of time, Ray Compiled Graphs can pre-allocate all necessary
resources ahead of time and greatly reduce the system overhead.
For example, if the actor `a` is on the same node as the driver, Ray Compiled Graphs uses shared memory instead of RPC to transfer data directly between the driver and the actor.

Currently, the DAG tasks run on a **background thread** of the involved actors.
An actor can only participate in one DAG at a time.
Normal tasks can still execute on the actors while the actors participate in a Compiled Graph, but these tasks execute on the main thread.

Once you're done, you can tear down the Compiled Graph by deleting it or explicitly calling `dag.teardown()`.
This allows reuse of the actors in a new Compiled Graph.

Specifying data dependencies

When creating the DAG, a `ray.dag.DAGNode` can be passed as an argument to other `.bind` calls to specify data dependencies.
For example, the following uses the preceding example to create a DAG that passes the same message from one actor to another:

  hello

Here is another example that passes the same message to both actors, which can then execute in parallel.
It uses ray.dag.MultiOutputNode to indicate that this DAG returns multiple outputs.
Then, dag.execute() returns multiple CompiledDAGRef objects, one per node:

  Execution takes 86.72196418046951 us

Be aware that:
* On the same actor, a Compiled Graph executes in order. If an actor has multiple tasks in the same Compiled Graph, it executes all of them to completion before executing on the next DAG input.
* Across actors in the same Compiled Graph, the execution may be pipelined. An actor may begin executing on the next DAG input while a downstream actor executes on the current one.
* Compiled Graphs currently only supports actor tasks. Non-actor tasks aren't supported.

`asyncio` support

If your Compiled Graph driver is running in an `asyncio` event loop, use the `async` APIs to ensure that executing
the Compiled Graph and getting the results doesn't block the event loop.
First, pass `enable_async=True` to the `dag.experimental_compile()`:

Next, use `execute_async` to invoke the Compiled Graph. Calling `await` on `execute_async` will return once
the input has been submitted, and it returns a future that can be used to get the result. Finally, 
use `await` to get the result of the Compiled Graph.

Execution and failure semantics

Like classic Ray Core, Ray Compiled Graph propagates exceptions to the final output.
In particular:

- **Application exceptions**: If an application task throws an exception, Compiled Graph
  wraps the exception in a RayTaskError and
  raises it when the caller calls ray.get() on the result. The thrown
  exception inherits from both RayTaskError
  and the original exception class.

- **System exceptions**: System exceptions include actor death or unexpected errors
  such as network errors. For actor death, Compiled Graph raises a
  ActorDiedError, and for other errors, it
  raises a RayChannelError.

The graph can still execute after application exceptions. However, the graph
automatically shuts down in the case of system exceptions. If an actor's death causes
the graph to shut down, the remaining actors stay alive.

For example, this example explicitly destroys an actor while it's participating in a Compiled Graph.
The remaining actors are reusable:

Execution Timeouts

Some errors, such as NCCL network errors, require additional handling to avoid hanging.
In the future, Ray may attempt to detect such errors, but currently as a fallback, it allows 
configurable timeouts for
compiled_dag.execute() and ray.get().

The default timeout is 10 seconds for both. Set the following environment variables
to change the default timeout:

- `RAY_CGRAPH_submit_timeout`: Timeout for compiled_dag.execute().
- `RAY_CGRAPH_get_timeout`: Timeout for ray.get().

ray.get() also has a timeout parameter to set timeout on a per-call basis.

CPU to GPU communication

With classic Ray Core, passing `torch.Tensors` between actors can become expensive, especially
when transferring between devices. This is because Ray Core doesn't know the final destination device.
Therefore, you may see unnecessary copies across devices other than the source and destination devices.

Ray Compiled Graph ships with native support for passing `torch.Tensors` between actors executing on different
devices. Developers can now use type hint annotations in the Compiled Graph declaration to indicate the final
destination device of a `torch.Tensor`.

In Ray Core, if you try to pass a CPU tensor from the driver,
the GPU actor receives a CPU tensor:

:skipif: True

    # This will fail because the driver passes a CPU copy of the tensor, 
    # and the GPU actor also receives a CPU copy.
    ray.get(actor.process.remote(torch.zeros(10)))

With Ray Compiled Graph, you can annotate DAG nodes with type hints to indicate that there may be a `torch.Tensor`
contained in the value:

Under the hood, the Ray Compiled Graph backend copies the `torch.Tensor` to the GPU assigned to the `GPUActor` by Ray Core.

Of course, you can also do this yourself, but there are advantages to using Compiled Graph instead:

- Ray Compiled Graph can minimize the number of data copies made. For example, passing from one CPU to
  multiple GPUs requires one copy to a shared memory buffer, and then one host-to-device copy per
  destination GPU.

- In the future, this can be further optimized through techniques such as
  [memory pinning](https://pytorch.org/docs/stable/generated/torch.Tensor.pin_memory.html),
  using zero-copy deserialization when the CPU is the destination, etc.

GPU to GPU communication

Ray Compiled Graphs supports NCCL-based transfers of CUDA `torch.Tensor` objects, avoiding any copies through Ray's CPU-based shared-memory object store.
With user-provided type hints, Ray prepares NCCL communicators and
operation scheduling ahead of time, avoiding deadlock and overlapping compute and communication.

Ray Compiled Graph uses [cupy](https://cupy.dev/) under the hood to support NCCL operations.
The cupy version affects the NCCL version. The Ray team is also planning to support custom communicators in the future, for example to support collectives across CPUs or to reuse existing collective groups.

First, create sender and receiver actors. Note that this example requires at least 2 GPUs.

To support GPU-to-GPU communication with NCCL, wrap the DAG node that contains the `torch.Tensor` that you want to transmit using the `with_tensor_transport` API hint:

Current limitations include:

* `torch.Tensor` and NVIDIA NCCL only
* Support for peer-to-peer transfers. Collective communication operations are coming soon.
* Communication operations are currently done synchronously. Overlapping compute and communication is an experimental feature.
