---
id: train.user-guides.monitoring-logging
title: Monitoring and Logging Metrics
topic_type: task
description: ''
subjects:
- train
- tune
- core
mentions:
- checkpoint
- driver
- trainer
- training-function
- trial
- worker
references: []
canonical_path: /en/latest/train/user-guides/monitoring-logging
source: https://github.com/ray-project/ray/blob/master/doc/source/train/user-guides/monitoring-logging.rst
license: Apache 2.0, The Ray Authors
---

Monitoring and Logging Metrics

Ray Train provides an API for attaching metrics to checkpoints from the training function by calling ray.train.report(metrics, checkpoint).
The results will be collected from the distributed workers and passed to the Ray Train driver process for book-keeping.

The primary use cases for reporting are:

* metrics (accuracy, loss, etc.) at the end of each training epoch. See train-dl-saving-checkpoints for usage examples.
* validating checkpoints on a validation set with a user-defined validation function. See train-validating-checkpoints for usage examples.

Only the result reported by the rank 0 worker is attached to the checkpoint.
However, in order to ensure consistency, `train.report()` acts as a barrier and must be called on each worker.
To aggregate results from multiple workers, see train-aggregating-results.

How to obtain and aggregate results from different workers?

In real applications, you may want to calculate optimization metrics besides accuracy and loss: recall, precision, Fbeta, etc.
You may also want to collect metrics from multiple workers. While Ray Train currently only reports metrics from the rank 0
worker, you can use third-party libraries or distributed primitives of your machine learning framework to report
metrics from multiple workers.

    
        Ray Train natively supports [TorchMetrics](https://torchmetrics.readthedocs.io/en/latest/), which provides a collection of machine learning metrics for distributed, scalable PyTorch models.

        Here is an example of reporting both the aggregated R2 score and mean train and validation loss from all workers.

        

(Deprecated) Reporting free-floating metrics

Reporting metrics with `ray.train.report(metrics, checkpoint=None)` from every worker writes the metrics to a Ray Tune log file (`progress.csv`, `result.json`)
and is accessible via the `Result.metrics_dataframe` on the ~ray.train.Result returned by `trainer.fit()`.

As of Ray 2.43, this behavior is deprecated and will not be supported in Ray Train V2,
which is an overhaul of Ray Train's implementation and select APIs.

Ray Train V2 only keeps a slim set of experiment tracking features that are necessary for fault tolerance, so it does not support reporting free-floating metrics that are not attached to checkpoints.
The recommendation for metric tracking is to report metrics directly from the workers to experiment tracking tools such as MLFlow and WandB.
See train-experiment-tracking-native for examples.

In Ray Train V2, reporting only metrics from all workers is a no-op. However, it is still possible to access the results reported by all workers to implement custom metric-handling logic.

To use Ray Tune Callbacks that depend on free-floating metrics reported by workers, run Ray Train as a single Ray Tune trial.

See the following resources for more information:

* [Train V2 REP](https://github.com/ray-project/enhancements/blob/main/reps/2024-10-18-train-tune-api-revamp/2024-10-18-train-tune-api-revamp.md): Technical details about the API changes in Train V2
* [Train V2 Migration Guide](https://github.com/ray-project/ray/issues/49454): Full migration guide for Train V2
