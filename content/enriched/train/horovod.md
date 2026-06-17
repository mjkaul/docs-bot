---
id: train.horovod
title: Get Started with Distributed Training using Horovod
topic_type: task
description: ''
subjects:
- train
mentions:
- scaling-config
- trainer
- training-function
references: []
canonical_path: /en/latest/train/horovod
source: https://github.com/ray-project/ray/blob/master/doc/source/train/horovod.rst
license: Apache 2.0, The Ray Authors
---

Get Started with Distributed Training using Horovod

Ray Train configures the Horovod environment and Rendezvous
server for you, allowing you to run your `DistributedOptimizer` training
script. See the [Horovod documentation](https://horovod.readthedocs.io/en/stable/index.html)
for more information.

Quickstart

Update your training function

First, update your training function to support distributed
training.

If you have a training function that already runs with the [Horovod Ray
Executor](https://horovod.readthedocs.io/en/stable/ray_include.html#horovod-ray-executor),
you shouldn't need to make any additional changes.

To onboard onto Horovod, visit the [Horovod guide](https://horovod.readthedocs.io/en/stable/index.html#get-started).

Create a HorovodTrainer

`Trainer`\s are the primary Ray Train classes to use to manage state and
execute training. For Horovod, use a ~ray.train.horovod.HorovodTrainer
that you can setup like this:

:hide:

    train_func = lambda: None

    from ray.train import ScalingConfig
    from ray.train.horovod import HorovodTrainer
    # For GPU Training, set `use_gpu` to True.
    use_gpu = False
    trainer = HorovodTrainer(
        train_func,
        scaling_config=ScalingConfig(use_gpu=use_gpu, num_workers=2)
    )

When training with Horovod, always use a HorovodTrainer,
irrespective of the training framework, for example, PyTorch or TensorFlow.

To customize the backend setup, you can pass a
~ray.train.horovod.HorovodConfig:

:skipif: True

    from ray.train import ScalingConfig
    from ray.train.horovod import HorovodTrainer, HorovodConfig

    trainer = HorovodTrainer(
        train_func,
        tensorflow_backend=HorovodConfig(...),
        scaling_config=ScalingConfig(num_workers=2),
    )

For more configurability, see the ~ray.train.data_parallel_trainer.DataParallelTrainer API.

Run a training function

With a distributed training function and a Ray Train `Trainer`, you are now
ready to start training.

:skipif: True

    trainer.fit()

Further reading

Ray Train's ~ray.train.horovod.HorovodTrainer replaces the distributed
communication backend of the native libraries with its own implementation.
Thus, the remaining integration points remain the same. If you're using Horovod
with PyTorch or Tensorflow,
refer to the respective guides for further configuration
and information.

If you are implementing your own Horovod-based training routine without using any of
the training libraries, read through the
User Guides, as you can apply much of the content
to generic use cases and adapt them easily.
