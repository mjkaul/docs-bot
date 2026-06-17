---
id: train.user-guides.results
title: Inspecting Training Results
topic_type: task
description: ''
subjects:
- train
- data
- serve
- tune
- core
mentions:
- batch-inference
- checkpoint
- task
- trainer
- training-function
- worker
references: []
canonical_path: /en/latest/train/user-guides/results
source: https://github.com/ray-project/ray/blob/master/doc/source/train/user-guides/results.rst
license: Apache 2.0, The Ray Authors
---

Inspecting Training Results

The return value of `trainer.fit()` is a ~ray.train.Result object.

The ~ray.train.Result object contains, among other information:

- The last reported checkpoint (to load the model) and its attached metrics
- Error messages, if any errors occurred
- Any data returned by the training function (on worker 0 only)

Viewing metrics

You can retrieve reported metrics that were attached to a checkpoint from the ~ray.train.Result object.

Common metrics include the training or validation loss, or prediction accuracies.

The metrics retrieved from the ~ray.train.Result object
correspond to those you passed to train.report
as an argument in your training function.

> **Note:** Persisting free-floating metrics reported via `ray.train.report(metrics, checkpoint=None)` is deprecated.
This also means that retrieving these metrics from the ~ray.train.Result object is deprecated.
Only metrics attached to checkpoints are persisted. See train-metric-only-reporting-deprecation for more details.

Last reported metrics

Use Result.metrics to retrieve the
metrics attached to the last reported checkpoint.

Dataframe of all reported metrics

Use Result.metrics_dataframe to retrieve
a pandas DataFrame of all metrics reported alongside checkpoints.

Returned data from train function

Use Result.return_value to retrieve any data
returned from worker 0's train function.

Retrieving checkpoints

You can retrieve checkpoints reported to Ray Train from the ~ray.train.Result
object.

Checkpoints contain all the information that is needed
to restore the training state. This usually includes the trained model.

You can use checkpoints for common downstream tasks such as
offline batch inference with Ray Data or
online model serving with Ray Serve.

The checkpoints retrieved from the ~ray.train.Result object
correspond to those you passed to train.report
as an argument in your training function.

Last saved checkpoint

Use Result.checkpoint to retrieve the
last checkpoint.

Other checkpoints

Sometimes you want to access an earlier checkpoint. For instance, if your loss increased
after more training due to overfitting, you may want to retrieve the checkpoint with
the lowest loss.

You can retrieve a list of all available checkpoints and their metrics with
Result.best_checkpoints

    See train-checkpointing for more information on checkpointing.

Accessing storage location

If you need to retrieve the results later, you can get the storage location
of the training run with Result.path.

This path will correspond to the storage_path you configured
in the ~ray.train.RunConfig. It will be a
(nested) subdirectory within that path, usually
of the form `TrainerName_date-string/TrainerName_id_00000_0_...`.

The result also contains a pyarrow.fs.FileSystem that can be used to
access the storage location, which is useful if the path is on cloud storage.

You can restore a result with Result.from_path:

Catching Errors

If an error occurred during training,
Result.error will be set and contain the exception
that was raised.

Finding results on persistent storage

All training results including reported metrics and checkpoints
are stored on the configured persistent storage.

See the persistent storage guide to configure this location
for your training run.
