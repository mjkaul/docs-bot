---
id: train.common.torch-configure-run
title: Configure scale and GPUs
topic_type: concept
description: ''
subjects:
- train
- tune
- core
mentions:
- checkpoint
- scaling-config
- trainer
- training-function
- worker
references: []
canonical_path: /en/latest/train/common/torch-configure-run
source: https://github.com/ray-project/ray/blob/master/doc/source/train/common/torch-configure-run.rst
license: Apache 2.0, The Ray Authors
---

Configure scale and GPUs

Outside of your training function, create a ~ray.train.ScalingConfig object to configure:

1. num_workers - The number of distributed training worker processes.
2. use_gpu - Whether each worker should use a GPU (or CPU).

    from ray.train import ScalingConfig
    scaling_config = ScalingConfig(num_workers=2, use_gpu=True)

For more details, see train_scaling_config.

Configure persistent storage

Create a ~ray.train.RunConfig object to specify the path where results
(including checkpoints and artifacts) will be saved.

    from ray.train import RunConfig

    # Local path (/some/local/path/unique_run_name)
    run_config = RunConfig(storage_path="/some/local/path", name="unique_run_name")

    # Shared cloud storage URI (s3://bucket/unique_run_name)
    run_config = RunConfig(storage_path="s3://bucket", name="unique_run_name")

    # Shared NFS path (/mnt/nfs/unique_run_name)
    run_config = RunConfig(storage_path="/mnt/nfs", name="unique_run_name")

> **Warning:** Specifying a *shared storage location* (such as cloud storage or NFS) is
*optional* for single-node clusters, but it is **required for multi-node clusters.**
Using a local path will raise an error
during checkpointing for multi-node clusters.

For more details, see persistent-storage-guide.

Launch a training job

Tying this all together, you can now launch a distributed training job
with a ~ray.train.torch.TorchTrainer.

:hide:

    from ray.train import ScalingConfig

    train_func = lambda: None
    scaling_config = ScalingConfig(num_workers=1)
    run_config = None

    from ray.train.torch import TorchTrainer

    trainer = TorchTrainer(
        train_func, scaling_config=scaling_config, run_config=run_config
    )
    result = trainer.fit()

Access training results

After training completes, a ~ray.train.Result object is returned which contains
information about the training run, including the metrics and checkpoints reported during training.

    result.metrics     # The metrics reported during training.
    result.checkpoint  # The latest checkpoint reported during training.
    result.path        # The path where logs are stored.
    result.error       # The exception that was raised, if training failed.

For more usage examples, see train-inspect-results.
