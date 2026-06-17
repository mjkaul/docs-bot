---
id: train.huggingface-accelerate
title: Get Started with Distributed Training using Hugging Face Accelerate
topic_type: task
description: ''
subjects:
- train
- core
mentions:
- scaling-config
- trainer
- training-function
- worker
references: []
canonical_path: /en/latest/train/huggingface-accelerate
source: https://github.com/ray-project/ray/blob/master/doc/source/train/huggingface-accelerate.rst
license: Apache 2.0, The Ray Authors
---

Get Started with Distributed Training using Hugging Face Accelerate

The ~ray.train.torch.TorchTrainer can help you easily launch your [Accelerate](https://huggingface.co/docs/accelerate)  training across a distributed Ray cluster.

You only need to run your existing training code with a TorchTrainer. You can expect the final code to look like this:

:skipif: True

    from accelerate import Accelerator

    def train_func():
        # Instantiate the accelerator
        accelerator = Accelerator(...)

        model = ...
        optimizer = ...
        train_dataloader = ...
        eval_dataloader = ...
        lr_scheduler = ...

        # Prepare everything for distributed training
        (
            model,
            optimizer,
            train_dataloader,
            eval_dataloader,
            lr_scheduler,
        ) = accelerator.prepare(
            model, optimizer, train_dataloader, eval_dataloader, lr_scheduler
        )

        # Start training
        ...

    from ray.train.torch import TorchTrainer
    from ray.train import ScalingConfig

    trainer = TorchTrainer(
        train_func,
        scaling_config=ScalingConfig(...),
        # If running in a multi-node cluster, this is where you
        # should configure the run's persistent storage that is accessible
        # across all worker nodes.
        # run_config=ray.train.RunConfig(storage_path="s3://..."),
        ...
    )
    trainer.fit()

> **Tip:** Model and data preparation for distributed training is completely handled by the [Accelerator](https://huggingface.co/docs/accelerate/main/en/package_reference/accelerator#accelerate.Accelerator)
object and its [Accelerator.prepare()](https://huggingface.co/docs/accelerate/main/en/package_reference/accelerator#accelerate.Accelerator.prepare)  method.

    Unlike with native PyTorch, **don't** call any additional Ray Train utilities
    like ~ray.train.torch.prepare_model or ~ray.train.torch.prepare_data_loader in your training function.

Configure Accelerate

In Ray Train, you can set configurations through the [accelerate.Accelerator](https://huggingface.co/docs/accelerate/main/en/package_reference/accelerator#accelerate.Accelerator)
object in your training function. Below are starter examples for configuring Accelerate.

    
        For example, to run DeepSpeed with Accelerate, create a [DeepSpeedPlugin](https://huggingface.co/docs/accelerate/main/en/package_reference/deepspeed)
        from a dictionary:

        

:skipif: True

            from accelerate import Accelerator, DeepSpeedPlugin

            DEEPSPEED_CONFIG = {
                "fp16": {
                    "enabled": True
                },
                "zero_optimization": {
                    "stage": 3,
                    "offload_optimizer": {
                        "device": "cpu",
                        "pin_memory": False
                    },
                    "overlap_comm": True,
                    "contiguous_gradients": True,
                    "reduce_bucket_size": "auto",
                    "stage3_prefetch_bucket_size": "auto",
                    "stage3_param_persistence_threshold": "auto",
                    "gather_16bit_weights_on_model_save": True,
                    "round_robin_gradients": True
                },
                "gradient_accumulation_steps": "auto",
                "gradient_clipping": "auto",
                "steps_per_print": 10,
                "train_batch_size": "auto",
                "train_micro_batch_size_per_gpu": "auto",
                "wall_clock_breakdown": False
            }

            def train_func():
                # Create a DeepSpeedPlugin from config dict
                ds_plugin = DeepSpeedPlugin(hf_ds_config=DEEPSPEED_CONFIG)

                # Initialize Accelerator
                accelerator = Accelerator(
                    ...,
                    deepspeed_plugin=ds_plugin,
                )

                # Start training
                ...

            from ray.train.torch import TorchTrainer
            from ray.train import ScalingConfig

            trainer = TorchTrainer(
                train_func,
                scaling_config=ScalingConfig(...),
                run_config=ray.train.RunConfig(storage_path="s3://..."),
                ...
            )
            trainer.fit()

    
        For PyTorch FSDP, create a [FullyShardedDataParallelPlugin](https://huggingface.co/docs/accelerate/main/en/package_reference/fsdp)
        and pass it to the Accelerator.

        

:skipif: True

            from torch.distributed.fsdp.fully_sharded_data_parallel import FullOptimStateDictConfig, FullStateDictConfig
            from accelerate import Accelerator, FullyShardedDataParallelPlugin

            def train_func():
                fsdp_plugin = FullyShardedDataParallelPlugin(
                    state_dict_config=FullStateDictConfig(
                        offload_to_cpu=False,
                        rank0_only=False
                    ),
                    optim_state_dict_config=FullOptimStateDictConfig(
                        offload_to_cpu=False,
                        rank0_only=False
                    )
                )

                # Initialize accelerator
                accelerator = Accelerator(
                    ...,
                    fsdp_plugin=fsdp_plugin,
                )

                # Start training
                ...

            from ray.train.torch import TorchTrainer
            from ray.train import ScalingConfig

            trainer = TorchTrainer(
                train_func,
                scaling_config=ScalingConfig(...),
                run_config=ray.train.RunConfig(storage_path="s3://..."),
                ...
            )
            trainer.fit()

Note that Accelerate also provides a CLI tool, `"accelerate config"`, to generate a configuration and launch your training
job with `"accelerate launch"`. However, it's not necessary here because Ray's `TorchTrainer` already sets up the Torch
distributed environment and launches the training function on all workers.

Next, see these end-to-end examples below for more details:

    
        .. dropdown:: Show Code

            
    
        .. dropdown:: Show Code

            

    If you're looking for more advanced use cases, check out this Llama-2 fine-tuning example:

    - [Fine-tuning Llama-2 series models with Deepspeed, Accelerate, and Ray Train.](https://github.com/ray-project/ray/tree/master/doc/source/templates/04_finetuning_llms_with_deepspeed)

You may also find these user guides helpful:

- train_scaling_config
- Configuration and Persistent Storage
- Saving and Loading Checkpoints
- How to use Ray Data with Ray Train

AccelerateTrainer Migration Guide

Before Ray 2.7, Ray Train's `AccelerateTrainer` API was the
recommended way to run Accelerate code. As a subclass of TorchTrainer,
the AccelerateTrainer takes in a configuration file generated by `accelerate config` and applies it to all workers.
Aside from that, the functionality of `AccelerateTrainer` is identical to `TorchTrainer`.

However, this caused confusion around whether this was the *only* way to run Accelerate code.
Because you can express the full Accelerate functionality with the `Accelerator` and `TorchTrainer` combination, the plan is to deprecate the `AccelerateTrainer` in Ray 2.8,
and it's recommend to run your  Accelerate code directly with `TorchTrainer`.
