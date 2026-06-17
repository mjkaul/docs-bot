---
id: tune.tutorials.tune-trial-checkpoints
title: How to Save and Load Trial Checkpoints
topic_type: task
description: ''
subjects:
- tune
- data
- serve
- train
- core
mentions:
- batch-inference
- checkpoint
- driver
- head-node
- search-algorithm
- task
- trainable
- trial
- tune-scheduler
references: []
canonical_path: /en/latest/tune/tutorials/tune-trial-checkpoints
source: https://github.com/ray-project/ray/blob/master/doc/source/tune/tutorials/tune-trial-checkpoints.rst
license: Apache 2.0, The Ray Authors
---

How to Save and Load Trial Checkpoints

Trial checkpoints are one of the three types of data stored by Tune.
These are user-defined and are meant to snapshot your training progress!

Trial-level checkpoints are saved via the Tune Trainable API: this is how you define your
custom training logic, and it's also where you'll define which trial state to checkpoint.
In this guide, we will show how to save and load checkpoints for Tune's Function Trainable and Class Trainable APIs,
as well as walk you through configuration options.

Function API Checkpointing

If using Ray Tune's Function API, one can save and load checkpoints in the following manner.
To create a checkpoint, use the ~ray.tune.Checkpoint.from_directory APIs.

In the above code snippet:

- We implement *checkpoint saving* with tune.report(..., checkpoint=checkpoint). Note that every checkpoint must be reported alongside a set of metrics -- this way, checkpoints can be ordered with respect to a specified metric.
- The saved checkpoint during training iteration `epoch` is saved to the path `<storage_path>/<exp_name>/<trial_name>/checkpoint_<epoch>` on the node on which training happens and can be further synced to a consolidated storage location depending on the storage configuration.
- We implement *checkpoint loading* with tune.get_checkpoint(). This will be populated with a trial's latest checkpoint whenever Tune restores a trial. This happens when (1) a trial is configured to retry after encountering a failure, (2) the experiment is being restored, and (3) the trial is being resumed after a pause (ex: PBT).

  .. TODO: for (1), link to tune fault tolerance guide. For (2), link to tune restore guide.

> **Note:** `checkpoint_frequency` and `checkpoint_at_end` will not work with Function API checkpointing.
These are configured manually with Function Trainable. For example, if you want to checkpoint every three
epochs, you can do so through:

    

See here for more information on creating checkpoints.

Class API Checkpointing

You can also implement checkpoint/restore using the Trainable Class API:

You can checkpoint with three different mechanisms: manually, periodically, and at termination.

Manual Checkpointing by Trainable

A custom Trainable can manually trigger checkpointing by returning `should_checkpoint: True`
(or `tune.result.SHOULD_CHECKPOINT: True`) in the result dictionary of `step`.
This can be especially helpful in spot instances:

In the above example, if `detect_instance_preemption` returns True, manual checkpointing can be triggered.

Manual Checkpointing by Tuner Callback

Similar to tune-class-trainable-checkpointing_manual-checkpointing,
you can also trigger checkpointing through Tuner Callback methods
by setting the `result["should_checkpoint"] = True` (or `result[tune.result.SHOULD_CHECKPOINT] = True`) flag
within the on_trial_result() method of your custom callback.
In contrast to checkpointing within the Trainable Class API, this approach decouples checkpointing logic from
the training logic, and provides access to all Trial instances allowing for more
complex checkpointing strategies.

Periodic Checkpointing

This can be enabled by setting `checkpoint_frequency=N` to checkpoint trials every *N* iterations, e.g.:

Checkpointing at Termination

The checkpoint_frequency may not coincide with the exact end of an experiment.
If you want a checkpoint to be created at the end of a trial, you can additionally set the `checkpoint_at_end=True`:

Configurations

Checkpointing can be configured through CheckpointConfig.
Some of the configurations do not apply to Function Trainable API, since checkpointing frequency
is determined manually within the user-defined training loop. See the compatibility matrix below.

   :header-rows: 1

   * -
     - Class API
     - Function API
   * - `num_to_keep`
     - ✅
     - ✅
   * - `checkpoint_score_attribute`
     - ✅
     - ✅
   * - `checkpoint_score_order`
     - ✅
     - ✅
   * - `checkpoint_frequency`
     - ✅
     - ❌
   * - `checkpoint_at_end`
     - ✅
     - ❌

Summary

In this user guide, we covered how to save and load trial checkpoints in Tune. Once checkpointing is enabled,
move onto one of the following guides to find out how to:

- Extract checkpoints from Tune experiment results
- Configure persistent storage options for a distributed Tune experiment

Appendix: Types of data stored by Tune

Experiment Checkpoints

Experiment-level checkpoints save the experiment state. This includes the state of the searcher,
the list of trials and their statuses (e.g., PENDING, RUNNING, TERMINATED, ERROR), and
metadata pertaining to each trial (e.g., hyperparameter configuration, some derived trial results
(min, max, last), etc).

The experiment-level checkpoint is periodically saved by the driver on the head node.
By default, the frequency at which it is saved is automatically
adjusted so that at most 5% of the time is spent saving experiment checkpoints,
and the remaining time is used for handling training results and scheduling.
This time can also be adjusted with the
TUNE_GLOBAL_CHECKPOINT_S environment variable.

Trial Checkpoints

Trial-level checkpoints capture the per-trial state. This often includes the model and optimizer states.
Following are a few uses of trial checkpoints:

- If the trial is interrupted for some reason (e.g., on spot instances), it can be resumed from the last state. No training time is lost.
- Some searchers or schedulers pause trials to free up resources for other trials to train in the meantime. This only makes sense if the trials can then continue training from the latest state.
- The checkpoint can be later used for other downstream tasks like batch inference.

Learn how to save and load trial checkpoints here.

Trial Results

Metrics reported by trials are saved and logged to their respective trial directories.
This is the data stored in CSV, JSON or Tensorboard (events.out.tfevents.*) formats.
that can be inspected by Tensorboard and used for post-experiment analysis.
