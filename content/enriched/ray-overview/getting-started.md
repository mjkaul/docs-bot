---
id: ray-overview.getting-started
title: Getting Started
topic_type: task
description: ''
subjects:
- core
- data
- tune
- train
mentions:
- actor
- dataset
- object-ref
- search-algorithm
- task
- trainer
- training-function
- trial
- worker
references: []
canonical_path: /en/latest/ray-overview/getting-started
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-overview/getting-started.md
license: Apache 2.0, The Ray Authors
---

# Getting Started

Ray is an open source unified framework for scaling AI and Python applications. It provides a simple, universal API for building distributed applications that can scale from a laptop to a cluster.

## What's Ray?

Ray simplifies distributed computing by providing:
- **Scalable compute primitives**: Tasks and actors for painless parallel programming
- **Specialized AI libraries**: Tools for common ML workloads like data processing, model training, hyperparameter tuning, and model serving
- **Unified resource management**: Seamless scaling from laptop to cloud with automatic resource handling

## Choose Your Path

Select the guide that matches your needs:
* **Scale ML workloads**: [Ray Libraries Quickstart](#libraries-quickstart)
* **Scale general Python applications**: [Ray Core Quickstart](#ray-core-quickstart)
* **Deploy to the cloud**: [Ray Clusters Quickstart](#ray-cluster-quickstart)
* **Debug and monitor applications**: [Debugging and Monitoring Quickstart](#debugging-and-monitoring-quickstart)

[code example]

## Ray AI Libraries Quickstart

Use individual libraries for ML workloads. Each library specializes in a specific part of the ML workflow, from data processing to model serving. Click on the dropdowns for your workload below.

``[code example]`{note}
To run this example, install Ray Data:

```bash
pip install -U "ray[data]"
```
````

[code example]

[code example]

[code example]
`````

```[code example]``{tab-set}

`[code example]bash
pip install -U "ray[train]" torch torchvision
```

Set up your dataset and model.

[code example]

Now define your single-worker PyTorch training function.

[code example]

This training function can be executed with:

[code example]

Convert this to a distributed multi-worker training function.

Use the ``ray.train.torch.prepare_model`` and
``ray.train.torch.prepare_data_loader`` utility functions to
set up your model and data for distributed training.
This automatically wraps the model with ``DistributedDataParallel``
and places it on the right device, and adds ``DistributedSampler`` to the DataLoaders.

[code example]

Instantiate a ``TorchTrainer``
with 4 workers, and use it to run the new training function.

[code example]

To accelerate the training job using GPU, make sure you have GPU configured, then set `use_gpu` to `True`. If you don't have a GPU environment, Anyscale provides a development workspace integrated with an autoscaling GPU cluster for this purpose.

<div class="anyscale-cta">
    <a href="https://console.anyscale.com/register/ha?render_flow=ray&utm_source=ray_docs&utm_medium=docs&utm_campaign=ray-doc-upsell&utm_content=get-started-train-torch">
        <img src="../_static/img/try-ray-on-anyscale.svg" alt="Try Ray on Anyscale">
    </a>
</div>

````

`[code example]bash
pip install -U "ray[train]" tensorflow
```

Set up your dataset and model.

[code example]

Now define your single-worker TensorFlow training function.

[code example]

This training function can be executed with:

[code example]

Now convert this to a distributed multi-worker training function.

1. Set the *global* batch size - each worker processes the same size
   batch as in the single-worker code.
2. Choose your TensorFlow distributed training strategy. This examples
   uses the ``MultiWorkerMirroredStrategy``.

[code example]

Instantiate a ``TensorflowTrainer``
with 4 workers, and use it to run the new training function.

[code example]

To accelerate the training job using GPU, make sure you have GPU configured, then set `use_gpu` to `True`. If you don't have a GPU environment, Anyscale provides a development workspace integrated with an autoscaling GPU cluster for this purpose.

<div class="anyscale-cta">
    <a href="https://console.anyscale.com/register/ha?render_flow=ray&utm_source=ray_docs&utm_medium=docs&utm_campaign=ray-doc-upsell&utm_content=get-started-train-tf">
        <img src="../_static/img/try-ray-on-anyscale.svg" alt="Try Ray on Anyscale">
    </a>
</div>

[code example]

````

`````

``````

``[code example]`{note}
To run this example, install Ray Tune:

```bash
pip install -U "ray[tune]"
```
````

This example runs a small grid search with an iterative training function.

[code example]

If TensorBoard is installed (`pip install tensorboard`), you can automatically visualize all trial results:

```bash
tensorboard --logdir ~/ray_results
```

[code example]

`````

``[code example]`{note}
To run this example, install Ray Serve and scikit-learn:

[code example]
````

This example runs serves a scikit-learn gradient boosting classifier.

[code example]

The response shows `{"result": "versicolor"}`.

[code example]

`````

``[code example]`{note}
To run this example, install `rllib` and either `tensorflow` or `pytorch`:

```bash
pip install -U "ray[rllib]" tensorflow  # or torch
```
You may also need CMake installed on your system.

````

[code example]

[code example]

`````

## Ray Core Quickstart

<a href="https://console.anyscale.com/register/ha?render_flow=ray&utm_source=ray_docs&utm_medium=docs&utm_campaign=ray-core-quickstart&redirectTo=/v2/template-preview/workspace-intro">
    <img src="../_static/img/run-on-anyscale.svg" alt="try-anyscale-quickstart-ray-quickstart">
</a>
<br></br>

Ray Core provides simple primitives for building and running distributed applications. It enables you to turn regular Python or Java functions and classes into distributed stateless tasks and stateful actors with just a few lines of code.

The examples below show you how to:
1. Convert Python functions to Ray tasks for parallel execution
2. Convert Python classes to Ray actors for distributed stateful computation

```[code example]``{tab-set}

`[code example]bash
pip install -U "ray"
```

Import Ray and and initialize it with `ray.init()`.
Then decorate the function with ``@ray.remote`` to declare that you want to run this function remotely.
Lastly, call the function with ``.remote()`` instead of calling it normally.
This remote call yields a future, a Ray _object reference_, that you can then fetch with ``ray.get``.

[code example]

````

`[code example]{note}
To run this example, add the [ray-api](https://mvnrepository.com/artifact/io.ray/ray-api) and [ray-runtime](https://mvnrepository.com/artifact/io.ray/ray-runtime) dependencies in your project.
```

Use `Ray.init` to initialize Ray runtime.
Then use `Ray.task(...).remote()` to convert any Java static method into a Ray task.
The task runs asynchronously in a remote worker process. The `remote` method returns an ``ObjectRef``,
and you can fetch the actual result with ``get``.

[code example]

In the above code block we defined some Ray Tasks. While these are great for stateless operations, sometimes you
must maintain the state of your application. You can do that with Ray Actors.

[code example]

````

`````

``````

```[code example]``{tab-set}

`[code example]bash
pip install -U "ray"
```

[code example]
````

`[code example]{note}
To run this example, add the [ray-api](https://mvnrepository.com/artifact/io.ray/ray-api) and [ray-runtime](https://mvnrepository.com/artifact/io.ray/ray-runtime) dependencies in your project.
```

[code example]

[code example]

````

`````

``````

## Ray Cluster Quickstart

Deploy your applications on Ray clusters on AWS, GCP, Azure, and more, often with minimal code changes to your existing code.

``[code example]bash
pip install -U "ray[default]" boto3
```

If you haven't already, configure your credentials as described in the [documentation for boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#guide-credentials).

Take this simple example that waits for individual nodes to join the cluster.

`[code example]{literalinclude} ../../yarn/example.py
:language: python
```
````
You can also download this example from the [GitHub repository](https://github.com/ray-project/ray/blob/master/doc/yarn/example.py).
Store it locally in a file called `example.py`.

To execute this script in the cloud, download [this configuration file](https://github.com/ray-project/ray/blob/master/python/ray/autoscaler/aws/example-minimal.yaml),
or copy it here:

`[code example]{literalinclude} ../../../python/ray/autoscaler/aws/example-minimal.yaml
:language: yaml
```
````

Assuming you have stored this configuration in a file called `cluster.yaml`, you can now launch an AWS cluster as follows:

```bash
ray submit cluster.yaml example.py --start
```

[code example]

`````

``[code example]{button-ref}  kuberay-index
:color: primary
:outline:
:expand:

Learn more about launching Ray Clusters on Kubernetes
```

`````

``[code example]{button-link} https://console.anyscale.com/register/ha?render_flow=ray&utm_source=ray_docs&utm_medium=docs&utm_campaign=ray-doc-upsell&utm_content=get-started-launch-ray-cluster
:color: primary
:outline:
:expand:

Try Ray on Anyscale
```

`````

## Debugging and Monitoring Quickstart

Use built-in observability tools to monitor and debug Ray applications and clusters. These tools help you understand your application's performance and identify bottlenecks.

``[code example]{image} https://raw.githubusercontent.com/ray-project/Images/master/docs/new-dashboard/Dashboard-overview.png
:align: center
```

`[code example]bash
pip install -U "ray[default]"
```
````
The dashboard automatically becomes available when running Ray scripts. Access the dashboard through the default URL, http://localhost:8265.

[code example]

`````

``[code example]`{note}
To get started with the state API, install the default installation as follows:

```bash
pip install -U "ray[default]"
```
````

Run the following code.

[code example]

See the summarized statistics of Ray tasks using ``ray summary tasks`` in a terminal.

[code example]

[code example]

[code example]

`````

## Learn More

Ray has a rich ecosystem of resources to help you learn more about distributed computing and AI scaling.

### Blog and Press

- [Modern Parallel and Distributed Python: A Quick Tutorial on Ray](https://medium.com/data-science/modern-parallel-and-distributed-python-a-quick-tutorial-on-ray-99f8d70369b8)
- [Why Every Python Developer Will Love Ray](https://www.datanami.com/2019/11/05/why-every-python-developer-will-love-ray/)
- [Ray: A Distributed System for AI (Berkeley Artificial Intelligence Research, BAIR)](http://bair.berkeley.edu/blog/2018/01/09/ray/)
- [10x Faster Parallel Python Without Python Multiprocessing](https://medium.com/data-science/10x-faster-parallel-python-without-python-multiprocessing-e5017c93cce1)
- [Implementing A Parameter Server in 15 Lines of Python with Ray](https://ray-project.github.io/2018/07/15/parameter-server-in-fifteen-lines.html)
- [Ray Distributed AI Framework Curriculum](https://rise.cs.berkeley.edu/blog/ray-intel-curriculum/)
- [RayOnSpark: Running Emerging AI Applications on Big Data Clusters with Ray and Analytics Zoo](https://medium.com/riselab/rayonspark-running-emerging-ai-applications-on-big-data-clusters-with-ray-and-analytics-zoo-923e0136ed6a)
- [First user tips for Ray](https://rise.cs.berkeley.edu/blog/ray-tips-for-first-time-users/)
- [Tune: a Python library for fast hyperparameter tuning at any scale](https://medium.com/data-science/fast-hyperparameter-tuning-at-scale-d428223b081c)
- [Cutting edge hyperparameter tuning with Ray Tune](https://medium.com/riselab/cutting-edge-hyperparameter-tuning-with-ray-tune-be6c0447afdf)
- [New Library Targets High Speed Reinforcement Learning](https://www.datanami.com/2018/02/01/rays-new-library-targets-high-speed-reinforcement-learning/)
- [Scaling Multi Agent Reinforcement Learning](http://bair.berkeley.edu/blog/2018/12/12/rllib/)
- [Functional RL with Keras and Tensorflow Eager](https://bair.berkeley.edu/blog/2019/10/14/functional-rl/)
- [How to Speed up Pandas by 4x with one line of code](https://www.kdnuggets.com/2019/11/speed-up-pandas-4x.html)
- [Quick Tip—Speed up Pandas using Modin](https://ericbrown.com/quick-tip-speed-up-pandas-using-modin.htm)
- [Ray Blog](https://medium.com/distributed-computing-with-ray)

### Videos

- [Unifying Large Scale Data Preprocessing and Machine Learning Pipelines with Ray Data \| PyData 2021](https://www.youtube.com/watch?v=wl4tvru9_Cg) [(slides)](https://docs.google.com/presentation/d/19F_wxkpo1JAROPxULmJHYZd3sKryapkbMd0ib3ndMiU/edit?usp=sharing)
- [Programming at any Scale with Ray \| SF Python Meetup Sept 2019](https://www.youtube.com/watch?v=LfpHyIXBhlE)
- [Ray for Reinforcement Learning \| Data Council 2019](https://www.youtube.com/watch?v=Ayc0ca150HI)
- [Scaling Interactive Pandas Workflows with Modin](https://www.youtube.com/watch?v=-HjLd_3ahCw)
- [Ray: A Distributed Execution Framework for AI \| SciPy 2018](https://www.youtube.com/watch?v=D_oz7E4v-U0)
- [Ray: A Cluster Computing Engine for Reinforcement Learning Applications \| Spark Summit](https://www.youtube.com/watch?v=xadZRRB_TeI)
- [RLlib: Ray Reinforcement Learning Library \| RISECamp 2018](https://www.youtube.com/watch?v=eeRGORQthaQ)
- [Enabling Composition in Distributed Reinforcement Learning \| Spark Summit 2018](https://www.youtube.com/watch?v=jAEPqjkjth4)
- [Tune: Distributed Hyperparameter Search \| RISECamp 2018](https://www.youtube.com/watch?v=38Yd_dXW51Q)

### Slides

- [Talk given at UC Berkeley DS100](https://docs.google.com/presentation/d/1sF5T_ePR9R6fAi2R6uxehHzXuieme63O2n_5i9m7mVE/edit?usp=sharing)
- [Talk given in October 2019](https://docs.google.com/presentation/d/13K0JsogYQX3gUCGhmQ1PQ8HILwEDFysnq0cI2b88XbU/edit?usp=sharing)
- [Talk given at RISECamp 2019](https://docs.google.com/presentation/d/1v3IldXWrFNMK-vuONlSdEuM82fuGTrNUDuwtfx4axsQ/edit?usp=sharing)

### Papers

-   [Ray 2.0 Architecture white paper](https://docs.google.com/document/d/1tBw9A4j62ruI5omIJbMxly-la5w4q_TjyJgJL_jN2fI/preview)
-   [Ray 1.0 Architecture white paper (old)](https://docs.google.com/document/d/1lAy0Owi-vPz2jEqBSaHNQcy2IBSDEHyXNOQZlGuj93c/preview)
-   [Exoshuffle: large-scale data shuffle in Ray](https://arxiv.org/abs/2203.05072)
-   [RLlib paper](https://arxiv.org/abs/1712.09381)
-   [RLlib flow paper](https://arxiv.org/abs/2011.12719)
-   [Tune paper](https://arxiv.org/abs/1807.05118)
-   [Ray paper (old)](https://arxiv.org/abs/1712.05889)
-   [Ray HotOS paper (old)](https://arxiv.org/abs/1703.03924)

If you encounter technical issues, post on the [Ray discussion forum](https://discuss.ray.io/). For general questions, announcements, and community discussions, join the [Ray community on Slack](https://www.ray.io/join-slack).
