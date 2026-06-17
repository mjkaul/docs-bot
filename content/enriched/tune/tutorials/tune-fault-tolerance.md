---
id: tune.tutorials.tune-fault-tolerance
title: How to Enable Fault Tolerance in Ray Tune
topic_type: task
description: ''
subjects:
- tune
- train
- data
- core
mentions:
- checkpoint
- dataset
- driver
- head-node
- object-store
- search-algorithm
- trainable
- trial
references: []
canonical_path: /en/latest/tune/tutorials/tune-fault-tolerance
source: https://github.com/ray-project/ray/blob/master/doc/source/tune/tutorials/tune-fault-tolerance.rst
license: Apache 2.0, The Ray Authors
---

How to Enable Fault Tolerance in Ray Tune

Fault tolerance is an important feature for distributed machine learning experiments
that can help mitigate the impact of node failures due to out of memory and out of disk issues.

With fault tolerance, users can:

- **Save time and resources by preserving training progress** even if a node fails.
- **Access the cost savings of preemptible spot instance nodes** in the distributed setting.

    In a *distributed* Tune experiment, a prerequisite to enabling fault tolerance
    is configuring some form of persistent storage where all trial results and
    checkpoints can be consolidated. See tune-storage-options.

In this guide, we will cover how to enable different types of fault tolerance offered by Ray Tune.

Experiment-level Fault Tolerance in Tune

At the experiment level, Tuner.restore
resumes a previously interrupted experiment from where it left off.

You should use Tuner.restore in the following cases:

1. The driver script that calls Tuner.fit() errors out (e.g., due to the head node running out of memory or out of disk).
2. The experiment is manually interrupted with `Ctrl+C`.
3. The entire cluster, and the experiment along with it, crashes due to an ephemeral error such as the network going down or Ray object store memory filling up.

> **Note:** Tuner.restore is *not* meant for resuming a terminated
experiment and modifying hyperparameter search spaces or stopping criteria.
Rather, experiment restoration is meant to resume and complete the *exact job*
that was previously submitted via Tuner.fit.

    For example, consider a Tune experiment configured to run for `10` training iterations,
    where all trials have already completed.
    Tuner.restore cannot be used to restore the experiment,
    change the number of training iterations to `20`, then continue training.

    Instead, this should be achieved by starting a *new* experiment and initializing
    your model weights with a checkpoint from the previous experiment.
    See this FAQ post for an example.

> **Note:** Bugs in your user-defined training loop cannot be fixed with restoration. Instead, the issue
that caused the experiment to crash in the first place should be *ephemeral*,
meaning that the retry attempt after restoring can succeed the next time.

Restore a Tune Experiment

Let's say your initial Tune experiment is configured as follows.
The actual training loop is just for demonstration purposes: the important detail is that
saving and loading checkpoints has been implemented in the trainable.

The results and checkpoints of the experiment are saved to `~/ray_results/tune_fault_tolerance_guide`,
as configured by ~ray.tune.RunConfig.
If the experiment has been interrupted due to one of the reasons listed above, use this path to resume:

> **Tip:** You can also restore the experiment from a cloud bucket path:

    
        tuner = tune.Tuner.restore(
            path="s3://cloud-bucket/tune_fault_tolerance_guide", trainable=trainable
        )

    See tune-storage-options.

Restore Configurations

Tune allows configuring which trials should be resumed, based on their status when the experiment was interrupted:

- Unfinished trials left in the `RUNNING` state will be resumed by default.
- Trials that have `ERRORED` can be resumed or retried from scratch.
- `TERMINATED` trials *cannot* be resumed.

Auto-resume

When running in a production setting, one may want a *single script* that (1) launches the
initial training run in the beginning and (2) restores the experiment if (1) already happened.

Use the Tuner.can_restore utility to accomplish this:

Running this script the first time will launch the initial training run.
Running this script the second time will attempt to resume from the outputs of the first run.

Tune Experiment Restoration with Ray Object References (Advanced)

Experiment restoration often happens in a different Ray session than the original run,
in which case Ray object references are automatically garbage collected.
If object references are saved along with experiment state (e.g., within each trial's config),
then attempting to retrieve these objects will not work properly after restoration:
the objects these references point to no longer exist.

To work around this, you must re-create these objects, put them in the Ray object store,
and then pass the new object references to Tune.

Example

Let's say we have some large pre-trained model that we want to use in some way in our training loop.
For example, this could be a image classification model used to calculate an Inception Score
to evaluate the quality of a generative model.
We may have multiple models that we want to tune over, where each trial samples one of the models to use.

To restore, we just need to re-specify the `param_space` via Tuner.restore:

> **Note:** If you're tuning over Ray Data, you'll also need to re-specify them in the `param_space`.
Ray Data can contain object references, so the same problems described above apply.

    See below for an example:

    
        ds_1 = ray.data.from_items([{"x": i, "y": 2 * i} for i in range(128)])
        ds_2 = ray.data.from_items([{"x": i, "y": 3 * i} for i in range(128)])

        param_space = {
            "datasets": {"train": tune.grid_search([ds_1, ds_2])},
        }

        tuner = tune.Tuner.restore(..., param_space=param_space)

Trial-level Fault Tolerance in Tune

Trial-level fault tolerance deals with individual trial failures in the cluster, which can be caused by:

- Running with preemptible spot instances.
- Ephemeral network connection issues.
- Nodes running out of memory or out of disk space.

Ray Tune provides a way to configure failure handling of individual trials with the ~ray.tune.FailureConfig.

Assuming that we're using the `trainable` from the previous example that implements
trial checkpoint saving and loading, here is how to configure ~ray.tune.FailureConfig:

When a trial encounters a runtime error, the above configuration will re-schedule that trial
up to `max_failures=3` times.

Similarly, if a node failure occurs for node `X` (e.g., pre-empted or lost connection),
this configuration will reschedule all trials that lived on node `X` up to `3` times.

Summary

In this user guide, we covered how to enable experiment-level and trial-level fault tolerance in Ray Tune.

See the following resources for more information:

- tune-storage-options
- tune-distributed-ref
- tune-trial-checkpoint
