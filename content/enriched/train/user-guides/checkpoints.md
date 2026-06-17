---
id: train.user-guides.checkpoints
title: Saving and Loading Checkpoints
topic_type: task
description: ''
subjects:
- train
- tune
- core
mentions:
- checkpoint
- trainer
- training-function
- worker
references: []
canonical_path: /en/latest/train/user-guides/checkpoints
source: https://github.com/ray-project/ray/blob/master/doc/source/train/user-guides/checkpoints.rst
license: Apache 2.0, The Ray Authors
---

Saving and Loading Checkpoints

Ray Train provides a way to snapshot training progress with Checkpoints.

This is useful for:

1. **Storing the best-performing model weights:** Save your model to persistent storage, and use it for downstream serving or inference.
2. **Fault tolerance:** Handle worker process and node failures in a long-running training job and leverage pre-emptible machines.
3. **Distributed checkpointing:** Ray Train checkpointing can be used to
   upload model shards from multiple workers in parallel.

Saving checkpoints during training

The Checkpoint is a lightweight interface provided
by Ray Train that represents a *directory* that exists on local or remote storage.

For example, a checkpoint could point to a directory in cloud storage:
`s3://my-bucket/my-checkpoint-dir`.
A locally available checkpoint points to a location on the local filesystem:
`/tmp/my-checkpoint-dir`.

Here's how you save a checkpoint in the training loop:

1. Write your model checkpoint to a local directory.

   - Since a Checkpoint just points to a directory, the contents are completely up to you.
   - This means that you can use any serialization format you want.
   - This makes it **easy to use familiar checkpoint utilities provided by training frameworks**, such as
     `torch.save`, `pl.Trainer.save_checkpoint`, Accelerate's `accelerator.save_model`,
     Transformers' `save_pretrained`, `tf.keras.Model.save`, etc.

2. Create a Checkpoint from the directory using Checkpoint.from_directory.

3. Report the checkpoint to Ray Train using ray.train.report(metrics, checkpoint=...).

   - The metrics reported alongside the checkpoint are used to keep track of the best-performing checkpoints.
   - This will **upload the checkpoint to persistent storage** if configured. See persistent-storage-guide.

    The lifecycle of a ~ray.train.Checkpoint, from being saved locally
    to disk to being uploaded to persistent storage via `train.report`.

As shown in the figure above, the best practice for saving checkpoints is to
first dump the checkpoint to a local temporary directory. Then, the call to `train.report`
uploads the checkpoint to its final persistent storage location.
Then, the local temporary directory can be safely cleaned up to free up disk space
(e.g., from exiting the `tempfile.TemporaryDirectory` context).

> **Tip:** In standard DDP training, where each worker has a copy of the full-model, you should
only save and report a checkpoint from a single worker to prevent redundant uploads.

    This typically looks like:

    
    If using parallel training strategies such as DeepSpeed Zero and FSDP, where
    each worker only has a shard of the full training state, you can save and report a checkpoint
    from each worker. See train-distributed-checkpointing for an example.

Here are a few examples of saving checkpoints with different training frameworks:

    
        
        
> **Tip:** You most likely want to unwrap the DDP model before saving it to a checkpoint.
`model.module.state_dict()` is the state dict without each key having a `"module."` prefix.

    
        Ray Train leverages PyTorch Lightning's `Callback` interface to report metrics
        and checkpoints. We provide a simple callback implementation that reports
        `on_train_epoch_end`.

        Specifically, on each train epoch end, it

        - collects all the logged metrics from `trainer.callback_metrics`
        - saves a checkpoint via `trainer.save_checkpoint`
        - reports to Ray Train via ray.train.report(metrics, checkpoint)

        
        You can always get the saved checkpoint path from result.checkpoint and
        result.best_checkpoints.

        For more advanced usage (e.g. reporting at different frequency, reporting
        customized checkpoint files), you can implement your own customized callback.
        Here is a simple example that reports a checkpoint every 3 epochs:

        

    
        Ray Train leverages Hugging Face Transformers Trainer's `Callback` interface
        to report metrics and checkpoints.

        **Option 1: Use Ray Train's default report callback**

        We provide a simple callback implementation ~ray.train.huggingface.transformers.RayTrainReportCallback that
        reports on checkpoint save. You can change the checkpointing frequency by `save_strategy` and `save_steps`.
        It collects the latest logged metrics and report them together with the latest saved checkpoint.

        
        Note that ~ray.train.huggingface.transformers.RayTrainReportCallback
        binds the latest metrics and checkpoints together,
        so users can properly configure `logging_strategy`, `save_strategy` and `evaluation_strategy`
        to ensure the monitoring metric is logged at the same step as checkpoint saving.

        For example, the evaluation metrics (`eval_loss` in this case) are logged during
        evaluation. If users want to keep the best 3 checkpoints according to `eval_loss`, they
        should align the saving and evaluation frequency. Below are two examples of valid configurations:

        

:skipif: True

            args = TrainingArguments(
                ...,
                evaluation_strategy="epoch",
                save_strategy="epoch",
            )

            args = TrainingArguments(
                ...,
                evaluation_strategy="steps",
                save_strategy="steps",
                eval_steps=50,
                save_steps=100,
            )

            # And more ...

        **Option 2: Implement your customized report callback**

        If you feel that Ray Train's default ~ray.train.huggingface.transformers.RayTrainReportCallback
        is not sufficient for your use case, you can also implement a callback yourself!
        Below is a example implementation that collects latest metrics
        and reports on checkpoint save.

        

        You can customize when (`on_save`, `on_epoch_end`, `on_evaluate`) and
        what (customized metrics and checkpoint files) to report by implementing your own
        Transformers Trainer callback.

Saving checkpoints from multiple workers (distributed checkpointing)

In model parallel training strategies where each worker only has a shard of the full-model,
you can save and report checkpoint shards in parallel from each worker.

    Distributed checkpointing in Ray Train. Each worker uploads its own checkpoint shard
    to persistent storage independently.

Distributed checkpointing is the best practice for saving checkpoints
when doing model-parallel training (e.g., DeepSpeed, FSDP, Megatron-LM).

There are two major benefits:

1. **It is faster, resulting in less idle time.** Faster checkpointing incentivizes more frequent checkpointing!

   Each worker can upload its checkpoint shard in parallel,
   maximizing the network bandwidth of the cluster. Instead of a single node
   uploading the full model of size `M`, the cluster distributes the load across
   `N` nodes, each uploading a shard of size `M / N`.

2. **Distributed checkpointing avoids needing to gather the full model onto a single worker's CPU memory.**

   This gather operation puts a large CPU memory requirement on the worker that performs checkpointing
   and is a common source of OOM errors.

Here is an example of distributed checkpointing with PyTorch:

> **Note:** Checkpoint files with the same name will collide between workers.
You can get around this by adding a rank-specific suffix to checkpoint files.

    Note that having filename collisions does not error, but it will result in the last
    uploaded version being the one that is persisted. This is fine if the file
    contents are the same across all workers.

    Model shard saving utilities provided by frameworks such as DeepSpeed will create
    rank-specific filenames already, so you usually do not need to worry about this.

Checkpoint upload modes

By default, when you call ~ray.train.report, Ray Train synchronously pushes
your checkpoint from `checkpoint.path` on local disk to `checkpoint_dir_name` on
your `storage_path`. This is equivalent to calling ~ray.train.report with
~ray.train.CheckpointUploadMode set to `ray.train.CheckpointUploadMode.SYNC`.

Asynchronous checkpoint uploading

You may want to upload your checkpoint asynchronously instead so that
the next training step can start in parallel. If so, you should use
`ray.train.CheckpointUploadMode.ASYNC`, which kicks off a new thread
to upload the checkpoint. This is helpful for larger
checkpoints that might take longer to upload, but might add unnecessary
complexity (see below) if you want to immediately upload only a small checkpoint.

Each `report` blocks until the previous `report`\'s checkpoint
upload completes before starting a new checkpoint upload thread. Ray Train does this
to avoid accumulating too many upload threads and potentially running out of memory.

Because `report` returns without waiting for the checkpoint upload to complete,
you must ensure that the local checkpoint directory stays alive until the checkpoint
upload completes. This means you can't use a temporary directory that Ray Train may
delete before the upload finishes, for example from `tempfile.TemporaryDirectory`.
`report` also exposes the `delete_local_checkpoint_after_upload` parameter, which
defaults to `True` if `checkpoint_upload_mode` is `ray.train.CheckpointUploadMode.ASYNC`.

    This figure illustrates the difference between synchronous and asynchronous
    checkpoint uploading.

Custom checkpoint uploading

~ray.train.report defaults to uploading from disk to the remote `storage_path`
with the PyArrow filesystem copying utilities before reporting the checkpoint to Ray Train.
If you would rather upload the checkpoint manually or with a third-party library
such as [Torch Distributed Checkpointing](https://docs.pytorch.org/docs/stable/distributed.checkpoint.html),
you have the following options:

    
        If you want to upload the checkpoint synchronously, you can first upload the checkpoint
        to the `storage_path` and then report a reference to the uploaded checkpoint with
        `ray.train.CheckpointUploadMode.NO_UPLOAD`.

        
    
        If you want to upload the checkpoint asynchronously, you can set `checkpoint_upload_mode`
        to `ray.train.CheckpointUploadMode.ASYNC` and pass a `checkpoint_upload_fn` to
        `ray.train.report`. This function takes the `Checkpoint` and `checkpoint_dir_name`
        passed to `ray.train.report` and returns the persisted `Checkpoint`.

        
        
> **Warning:** In your `checkpoint_upload_fn`, you should not call `ray.train.report`, which may
lead to unexpected behavior. You should also avoid collective operations, such as
~ray.train.report or `model.state_dict()`, which can cause deadlocks. Finally,
the upload function should only the return a checkpoint object once all checkpoint data
has been saved.

        
> **Note:** Do not pass a `checkpoint_upload_fn` with `checkpoint_upload_mode=ray.train.CheckpointUploadMode.NO_UPLOAD`
because Ray Train will simply ignore `checkpoint_upload_fn`. You can pass a `checkpoint_upload_fn` with
`checkpoint_upload_mode=ray.train.CheckpointUploadMode.SYNC`, but this is equivalent to uploading the
checkpoint yourself and reporting the checkpoint with `ray.train.CheckpointUploadMode.NO_UPLOAD`.

Configure checkpointing

Ray Train provides some configuration options for checkpointing via ~ray.train.CheckpointConfig.
The primary configuration is keeping only the top `K` checkpoints with respect to a metric.
Lower-performing checkpoints are deleted to save storage space. By default, all checkpoints are kept.

> **Note:** If you want to save the top `num_to_keep` checkpoints with respect to a metric via
~ray.train.CheckpointConfig,
please ensure that the metric is always reported together with the checkpoints.

Using checkpoints during training

During training, you may want to access checkpoints you've reported and their associated metrics
from training workers for a variety of reasons, such as
reporting the best checkpoint so far to an experiment tracker. You can do this by calling
~ray.train.get_all_reported_checkpoints from within your training function. This function returns
a list of ~ray.train.ReportedCheckpoint objects that represent all the
~ray.train.Checkpoint\s and their associated metrics that you've reported so far
and have been kept based on the checkpoint configuration.

This function supports two consistency modes:

- `CheckpointConsistencyMode.COMMITTED`: Block until the checkpoint from the latest `ray.train.report`
  has been uploaded to persistent storage and committed.
- `CheckpointConsistencyMode.VALIDATED`: Block until the checkpoint from the latest `ray.train.report`
  has been uploaded to persistent storage, committed, and validated (see train-validating-checkpoints).
  This is the default consistency mode and has the same behavior as `CheckpointConsistencyMode.COMMITTED`
  if your report did not kick off validation.

Using checkpoints after training

The latest saved checkpoint can be accessed with Result.checkpoint.

The full list of persisted checkpoints can be accessed with Result.best_checkpoints.
If CheckpointConfig(num_to_keep) is set, this list will contain the best `num_to_keep` checkpoints.

See train-inspect-results for a full guide on inspecting training results.

Checkpoint.as_directory
and Checkpoint.to_directory
are the two main APIs to interact with Train checkpoints:

For Lightning and Transformers, if you are using the default `RayTrainReportCallback` for checkpoint saving in your training function,
you can retrieve the original checkpoint files as below:

    
        
    
        

Restore training state from a checkpoint

In order to enable fault tolerance, you should modify your training loop to restore
training state from a ~ray.train.Checkpoint.

The Checkpoint to restore from can be accessed in the
training function with ray.train.get_checkpoint.

The checkpoint returned by ray.train.get_checkpoint is populated
as the latest reported checkpoint during automatic failure recovery.

See train-fault-tolerance for more details on restoration and fault tolerance.

    
        

    
        

> **Note:** In these examples, Checkpoint.as_directory
is used to view the checkpoint contents as a local directory.

    *If the checkpoint points to a local directory*, this method just returns the
    local directory path without making a copy.

    *If the checkpoint points to a remote directory*, this method will download the
    checkpoint to a local temporary directory and return the path to the temporary directory.

    **If multiple processes on the same node call this method simultaneously,**
    only a single process will perform the download, while the others
    wait for the download to finish. Once the download finishes, all processes receive
    the same local (temporary) directory to read from.

    Once all processes have finished working with the checkpoint, the temporary directory
    is cleaned up.
