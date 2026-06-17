---
id: tune.getting-started
title: Getting Started with Ray Tune
topic_type: task
description: ''
subjects:
- tune
- core
- train
mentions:
- actor
- search-algorithm
- search-space
- training-function
- trial
- tune-scheduler
references: []
canonical_path: /en/latest/tune/getting-started
source: https://github.com/ray-project/ray/blob/master/doc/source/tune/getting-started.rst
license: Apache 2.0, The Ray Authors
---

Getting Started with Ray Tune

This tutorial will walk you through the process of setting up a Tune experiment.
To get started, we take a PyTorch model and show you how to leverage Ray Tune to
optimize the hyperparameters of this model.
Specifically, we'll leverage early stopping and Bayesian Optimization via HyperOpt to do so.

    please [let us know](https://github.com/ray-project/ray/issues/new/choose)!

To run this example, you will need to install the following:

    $ pip install "ray[tune]" torch torchvision

Setting Up a PyTorch Model to Tune

To start off, let's first import some dependencies.
We import some PyTorch and TorchVision modules to help us create a model and train it.
Also, we'll import Ray Tune to help us optimize the model.
As you can see we use a so-called scheduler, in this case the `ASHAScheduler`
that we will use for tuning the model later in this tutorial.

Then, let's define a simple PyTorch model that we'll be training.
If you're not familiar with PyTorch, the simplest way to define a model is to implement a `nn.Module`.
This requires you to set up your model with `__init__` and then implement a `forward` pass.
In this example we're using a small convolutional neural network consisting of one 2D convolutional layer, a fully
connected layer, and a softmax function.

Below, we have implemented functions for training and evaluating your PyTorch model.
We define a `train` and a `test` function for that purpose.
If you know how to do this, skip ahead to the next section.

    

Setting up a `Tuner` for a Training Run with Tune

Below, we define a function that trains the PyTorch model for multiple epochs.
This function will be executed on a separate Ray Actor (process) underneath the hood,
so we need to communicate the performance of the model back to Tune (which is on the main Python process).

To do this, we call tune.report() in our training function,
which sends the performance value back to Tune. Since the function is executed on the separate process,
make sure that the function is serializable by Ray.

Let's run one trial by calling Tuner.fit and randomly sample
from a uniform distribution for learning rate and momentum.

`Tuner.fit` returns an ResultGrid object.
You can use this to plot the performance of this trial.

    To limit the number of concurrent trials, use the ConcurrencyLimiter.

Early Stopping with Adaptive Successive Halving (ASHAScheduler)

Let's integrate early stopping into our optimization process. Let's use ASHA, a scalable algorithm for `principled early stopping`_.

On a high level, ASHA terminates trials that are less promising and allocates more time and resources to more promising trials.
As our optimization process becomes more efficient, we can afford to **increase the search space by 5x**, by adjusting the parameter `num_samples`.

ASHA is implemented in Tune as a "Trial Scheduler".
These Trial Schedulers can early terminate bad trials, pause trials, clone trials, and alter hyperparameters of a running trial.
See the TrialScheduler documentation for more details of available schedulers and library integrations.

You can run the below in a Jupyter notebook to visualize trial progress.

You can also use TensorBoard for visualizing results.

    $ tensorboard --logdir {logdir}

Using Search Algorithms in Tune

In addition to TrialSchedulers, you can further optimize your hyperparameters
by using an intelligent search technique like Bayesian Optimization.
To do this, you can use a Tune Search Algorithm.
Search Algorithms leverage optimization algorithms to intelligently navigate the given hyperparameter space.

Note that each library has a specific way of defining the search space.

Evaluating Your Model after Tuning

You can evaluate the best trained model using the ExperimentAnalysis object to retrieve the best model:

Next Steps

* Check out the Tune tutorials for guides on using Tune with your preferred machine learning library.
* Browse our gallery of examples to see how to use Tune with PyTorch, XGBoost, Tensorflow, etc.
* [Let us know](https://github.com/ray-project/ray/issues) if you ran into issues or have any questions by opening an issue on our GitHub.
* To check how your application is doing, you can use the Ray dashboard.
