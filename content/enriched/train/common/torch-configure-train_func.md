---
id: train.common.torch-configure-train_func
title: Torch Configure Train Func
topic_type: concept
description: ''
subjects:
- train
- data
- core
mentions:
- dataset
- trainer
- training-function
- worker
references: []
canonical_path: /en/latest/train/common/torch-configure-train_func
source: https://github.com/ray-project/ray/blob/master/doc/source/train/common/torch-configure-train_func.rst
license: Apache 2.0, The Ray Authors
---

First, update your training code to support distributed training.
Begin by wrapping your code in a training function:

:skipif: True

    def train_func():
        # Your model training code here.
        ...

Each distributed training worker executes this function.

You can also specify the input argument for `train_func` as a dictionary via the Trainer's `train_loop_config`. For example:

:skipif: True

    def train_func(config):
        lr = config["lr"]
        num_epochs = config["num_epochs"]

    config = {"lr": 1e-4, "num_epochs": 10}
    trainer = ray.train.torch.TorchTrainer(train_func, train_loop_config=config, ...)

> **Warning:** Avoid passing large data objects through `train_loop_config` to reduce the
serialization and deserialization overhead. Instead, it's preferred to
initialize large objects (e.g. datasets, models) directly in `train_func`.

    
         def load_dataset():
             # Return a large in-memory dataset
             ...

         def load_model():
             # Return a large in-memory model instance
             ...

        -config = {"data": load_dataset(), "model": load_model()}

         def train_func(config):
        -    data = config["data"]
        -    model = config["model"]

        +    data = load_dataset()
        +    model = load_model()
             ...

         trainer = ray.train.torch.TorchTrainer(train_func, train_loop_config=config, ...)
