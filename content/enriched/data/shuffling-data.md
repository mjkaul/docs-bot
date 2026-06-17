---
id: data.shuffling-data
title: Shuffling Data
topic_type: task
description: ''
subjects:
- data
- core
mentions:
- dataset
- task
- worker
references: []
canonical_path: /en/latest/data/shuffling-data
source: https://github.com/ray-project/ray/blob/master/doc/source/data/shuffling-data.rst
license: Apache 2.0, The Ray Authors
---

Shuffling Data

When consuming or iterating over Ray Datasets, it can be useful to
shuffle or randomize the order of data (for example, randomizing data ingest order during ML training).
This guide shows several different methods of shuffling data with Ray Data and their respective trade-offs.

Types of shuffling

Ray Data provides several different options for shuffling data, trading off the granularity of shuffle
control with memory consumption and runtime. The list below presents options in increasing order of
resource consumption and runtime. Choose the most appropriate method for your use case.

Shuffle the ordering of files

To randomly shuffle the ordering of input files before reading, call a read function function that supports shuffling, such as
~ray.data.read_images, and use the `shuffle="files"` parameter. This randomly assigns
input files to workers for reading.

This is the fastest "shuffle" option: it's purely a metadata operation---the system random-shuffles the list of files constituting the dataset before
fetching them with reading tasks. This option, however, doesn't shuffle the rows inside files, so the randomness might not be
sufficient for your needs in case of files with the large number of rows.

    import ray

    ds = ray.data.read_images(
        "s3://anonymous@ray-example-data/image-datasets/simple",
        shuffle="files",
    )

Local buffer shuffle

To locally shuffle a subset of rows using iteration methods, such as ~ray.data.Dataset.iter_batches,
~ray.data.Dataset.iter_torch_batches, and ~ray.data.Dataset.iter_tf_batches,
specify `local_shuffle_buffer_size`.

This shuffles up to a `local_shuffle_buffer_size` number of rows buffered during iteration. See more details in
Iterating over batches with shuffling.

This is slower than files shuffling, and shuffles rows locally without
network transfer. You can use this local shuffle buffer together with shuffling
ordering of files. See Shuffle the ordering of files.

    import ray

    ds = ray.data.read_images("s3://anonymous@ray-example-data/image-datasets/simple")

    for batch in ds.iter_batches(
        batch_size=2,
        batch_format="numpy",
        local_shuffle_buffer_size=250,
    ):
        print(batch)

> **Tip:** If you observe reduced throughput when using `local_shuffle_buffer_size`,
check the total time spent in batch creation by
examining the `ds.stats()` output (`In batch formatting`, under
`Batch iteration time breakdown`). If this time is significantly larger than the
time spent in other steps, decrease `local_shuffle_buffer_size` or turn off the local
shuffle buffer altogether and only shuffle the ordering of files.

`map_batches` shuffle

To shuffle data as a separate data stage, use ~ray.data.Dataset.map_batches
with a shuffle function that randomly permutes rows within each batch. Compared to local
buffer shuffle, this approach has several advantages:

- It **decouples shuffling from the iterator**, running as a separate Ray Data operator
  that doesn't block downstream CPU/GPU processing.
- Ray Data's resource management automatically schedules shuffle tasks based on available
  cluster resources (CPU, memory), avoiding resource contention.
- The shuffle work can happen in parallel across multiple machines, making it more scalable
  for large datasets.

The `batch_size` parameter controls the shuffle window---a larger value shuffles more rows
together for better randomness but requires more memory.

> **Important:** Always set the `memory` parameter when using large batch sizes to avoid out-of-memory
errors. Estimate it as `batch_size * row_bytes`:

    import numpy as np
    import pyarrow as pa
    import ray

    def random_shuffle(batch: pa.Table) -> pa.Table:
        indices = np.random.permutation(len(batch))
        return batch.take(indices)

    row_bytes = 4096
    shuffle_memory = int(2**30)  # 1 GB shuffle window
    batch_size = int(shuffle_memory / row_bytes)

    ds = ray.data.range(1000)
    ds = ds.map_batches(
        random_shuffle,
        batch_size=batch_size,
        batch_format="pyarrow",
        memory=shuffle_memory,
    )
    ds.take(10)

> **Tip:** Combine `map_batches` shuffle with file order shuffling for
additional randomness. File order shuffling randomizes which files are read first, while
`map_batches` shuffle randomizes rows within each shuffle window.

Comparing local buffer shuffle and `map_batches` shuffle

The following benchmark compares steady-state training throughput between local buffer shuffle
and `map_batches` shuffle on a synthetic workload (`ray.data.range_tensor`, ~4 KB/row, 4 GPU
workers, batch size 4096, 200 steps with 100 warmup):

   :header-rows: 1
   :widths: 30 20 15

   * - Method
     - Throughput (rows/s)
     - % of baseline
   * - No shuffle (baseline)
     - 1,759,282
     - 100%
   * - Local buffer shuffle 1 GB
     - 225,181
     - 13%
   * - Local buffer shuffle 2 GB
     - 220,644
     - 13%
   * - Local buffer shuffle 3 GB
     - 153,256
     - 9%
   * - `map_batches` shuffle 1 GB
     - 1,400,734
     - 80%
   * - `map_batches` shuffle 2 GB
     - 1,460,037
     - 83%
   * - `map_batches` shuffle 3 GB
     - 1,588,428
     - 90%

Randomizing block order

This option randomizes the order of blocks in a dataset. While applying this operation alone doesn't involve heavy computation
and communication, it requires Ray Data to materialize all blocks in memory before actually randomizing their ordering in the queue for subsequent operation.

    is primarily relevant in cases when the system yields blocks from relatively small set of very large files.

To perform block order shuffling, use randomize_block_order.

import ray

    ds = ray.data.read_text(
        "s3://anonymous@ray-example-data/sms_spam_collection_subset.txt"
    )

    # Randomize the block order of this dataset.
    ds = ds.randomize_block_order()

Global shuffle

To shuffle all rows globally, across the whole dataset, multiple options are available

1. *Random shuffling*: invoking ~ray.data.Dataset.random_shuffle essentially permutes and shuffles individual rows
from existing blocks into the new ones using an optionally provided seed.
2. (**New in 2.46**) *Key-based repartitioning*: invoking ~ray.data.Dataset.repartition with `keys` parameter triggers
hash-shuffle operation, shuffling the rows based on the hash of the values in the provided key columns, providing
deterministic way of co-locating rows based on the hash of the column values.

Note that shuffle is an expensive operation requiring materializing of the whole dataset in memory as well as serving as a synchronization
barrier---subsequent operators won't be able to start executing until shuffle completion.

Example of random shuffling with seed:

    import ray

    ds = ray.data.read_images("s3://anonymous@ray-example-data/image-datasets/simple")

    # Random shuffle with seed
    random_shuffled_ds = ds.random_shuffle(seed=123)

Example of hash shuffling based on column `id`:

    import ray
    from ray.data.context import DataContext, ShuffleStrategy

    # First enable hash-shuffle as shuffling strategy
    DataContext.get_current().shuffle_strategy = ShuffleStrategy.HASH_SHUFFLE

    # Hash-shuffle
    hash_shuffled_ds = ds.repartition(keys="id", num_blocks=200)

Advanced: Optimizing shuffles

    [file a Ray Data issue on GitHub](https://github.com/ray-project/ray/issues/new?assignees=&labels=bug%2Ctriage%2Cdata&projects=&template=bug-report.yml&title=[data]+).

When should you use global per-epoch shuffling?

Use global per-epoch shuffling only if your model is sensitive to the
randomness of the training data. Based on a
[theoretical foundation](https://arxiv.org/abs/1709.10432), all
gradient-descent-based model trainers benefit from improved global shuffle quality.
In practice, the benefit's particularly pronounced for tabular data/models.
However, the more global the shuffle is, the more expensive the shuffling operation.
The increase compounds with distributed data-parallel training on a multi-node cluster due
to data transfer costs. This cost can be prohibitive when using very large datasets.

The best route for determining the best tradeoff between preprocessing time and cost and
per-epoch shuffle quality is to measure the precision gain per training step for your
particular model under different shuffling policies such as no shuffling, local shuffling, or global shuffling.

As long as your data loading and shuffling throughput is higher than your training throughput, your GPU should
saturate. If you have shuffle-sensitive models, push the
shuffle quality higher until you reach this threshold.

Enabling push-based shuffle

Some Dataset operations require a *shuffle* operation, meaning that the system shuffles data from all of the input partitions to all of the output partitions.
These operations include Dataset.random_shuffle,
Dataset.sort and Dataset.groupby.
For example, during a sort operation, the system reorders data between blocks and therefore requires shuffling across partitions.
Shuffling can be challenging to scale to large data sizes and clusters, especially when the total dataset size can't fit into memory.

Ray Data provides an alternative shuffle implementation known as push-based shuffle for improving large-scale performance.
Try this out if your dataset has more than 1000 blocks or is larger than 1 TB in size.

To try this out locally or on a cluster, you can start with the [nightly release test](https://github.com/ray-project/ray/blob/master/release/nightly_tests/dataset/sort_benchmark.py) that Ray runs for Dataset.random_shuffle and Dataset.sort.
To get an idea of the performance you can expect, here are some run time results for Dataset.random_shuffle on 1-10 TB of data on 20 machines - m5.4xlarge instances on AWS EC2, each with 16 vCPUs, 64 GB RAM.

To try out push-based shuffle, set the environment variable `RAY_DATA_PUSH_BASED_SHUFFLE=1` when running your application:

    $ wget https://raw.githubusercontent.com/ray-project/ray/master/release/nightly_tests/dataset/sort_benchmark.py
    $ RAY_DATA_PUSH_BASED_SHUFFLE=1 python sort_benchmark.py --num-partitions=10 --partition-size=1e7

    # Dataset size: 10 partitions, 0.01GB partition size, 0.1GB total
    # [dataset]: Run `pip install tqdm` to enable progress reporting.
    # 2022-05-04 17:30:28,806	INFO push_based_shuffle.py:118 -- Using experimental push-based shuffle.
    # Finished in 9.571171760559082
    # ...

You can also specify the shuffle implementation during program execution by
setting the `DataContext.use_push_based_shuffle` flag:

:hide:

    import ray
    ray.shutdown()

    import ray

    ctx = ray.data.DataContext.get_current()
    ctx.use_push_based_shuffle = True

    ds = (
        ray.data.range(1000)
        .random_shuffle()
    )

Large-scale shuffles can take a while to finish.
For debugging purposes, shuffle operations support executing only part of the shuffle, so that you can collect an execution profile more quickly.
Here is an example that shows how to limit a random shuffle operation to two output blocks:

:hide:

    import ray
    ray.shutdown()

    import ray

    ctx = ray.data.DataContext.get_current()
    ctx.set_config(
        "debug_limit_shuffle_execution_to_num_blocks", 2
    )

    ds = (
        ray.data.range(1000, override_num_blocks=10)
        .random_shuffle()
        .materialize()
    )
    print(ds.stats())

    Operator 1 ReadRange->RandomShuffle: executed in 0.08s

        Suboperator 0 ReadRange->RandomShuffleMap: 2/2 blocks executed
        ...
