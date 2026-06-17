---
id: tune.tutorials.tune-search-spaces
title: Working with Tune Search Spaces
topic_type: task
description: ''
subjects:
- tune
mentions:
- search-space
- trainable
- trial
references: []
canonical_path: /en/latest/tune/tutorials/tune-search-spaces
source: https://github.com/ray-project/ray/blob/master/doc/source/tune/tutorials/tune-search-spaces.rst
license: Apache 2.0, The Ray Authors
---

Working with Tune Search Spaces

Tune has a native interface for specifying search spaces.
You can specify the search space via `Tuner(param_space=...)`.

Thereby, you can either use the `tune.grid_search` primitive to use grid search:

    tuner = tune.Tuner(
        trainable,
        param_space={"bar": tune.grid_search([True, False])})
    results = tuner.fit()

Or you can use one of the random sampling primitives to specify distributions (/tune/api/search_space):

    tuner = tune.Tuner(
        trainable,
        param_space={
            "param1": tune.choice([True, False]),
            "bar": tune.uniform(0, 10),
            "alpha": tune.sample_from(lambda _: np.random.uniform(100) ** 2),
            "const": "hello"  # It is also ok to specify constant values.
        })
    results = tuner.fit()

    interface, as some search algorithms may not be compatible.

To sample multiple times/run multiple trials, specify `tune.RunConfig(num_samples=N`.
If `grid_search` is provided as an argument, the *same* grid will be repeated `N` times.

    # 13 different configs.
    tuner = tune.Tuner(trainable, tune_config=tune.TuneConfig(num_samples=13), param_space={
        "x": tune.choice([0, 1, 2]),
        }
    )
    tuner.fit()

    # 13 different configs.
    tuner = tune.Tuner(trainable, tune_config=tune.TuneConfig(num_samples=13), param_space={
        "x": tune.choice([0, 1, 2]),
        "y": tune.randn([0, 1, 2]),
        }
    )
    tuner.fit()

    # 4 different configs.
    tuner = tune.Tuner(trainable, tune_config=tune.TuneConfig(num_samples=1), param_space={"x": tune.grid_search([1, 2, 3, 4])})
    tuner.fit()

    # 3 different configs.
    tuner = tune.Tuner(trainable, tune_config=tune.TuneConfig(num_samples=1), param_space={"x": tune.grid_search([1, 2, 3])})
    tuner.fit()

    # 6 different configs.
    tuner = tune.Tuner(trainable, tune_config=tune.TuneConfig(num_samples=2), param_space={"x": tune.grid_search([1, 2, 3])})
    tuner.fit()

    # 9 different configs.
    tuner = tune.Tuner(trainable, tune_config=tune.TuneConfig(num_samples=1), param_space={
        "x": tune.grid_search([1, 2, 3]),
        "y": tune.grid_search([a, b, c])}
    )
    tuner.fit()

    # 18 different configs.
    tuner = tune.Tuner(trainable, tune_config=tune.TuneConfig(num_samples=2), param_space={
        "x": tune.grid_search([1, 2, 3]),
        "y": tune.grid_search([a, b, c])}
    )
    tuner.fit()

    # 45 different configs.
    tuner = tune.Tuner(trainable, tune_config=tune.TuneConfig(num_samples=5), param_space={
        "x": tune.grid_search([1, 2, 3]),
        "y": tune.grid_search([a, b, c])}
    )
    tuner.fit()

Note that grid search and random search primitives are inter-operable.
Each can be used independently or in combination with each other.

    # 6 different configs.
    tuner = tune.Tuner(trainable, tune_config=tune.TuneConfig(num_samples=2), param_space={
        "x": tune.sample_from(...),
        "y": tune.grid_search([a, b, c])
        }
    )
    tuner.fit()

In the below example, `num_samples=10` repeats the 3x3 grid search 10 times,
for a total of 90 trials, each with randomly sampled values of `alpha` and `beta`.

:emphasize-lines: 12

    tuner = tune.Tuner(
        my_trainable,
        run_config=tune.RunConfig(name="my_trainable"),
        # num_samples will repeat the entire config 10 times.
        tune_config=tune.TuneConfig(num_samples=10),
        param_space={
            # `sample_from` creates a generator to call the lambda once per trial.
            "alpha": tune.sample_from(lambda _: np.random.uniform(100)),
            # `sample_from` also supports "conditional search spaces"
            "beta": tune.sample_from(lambda config: config["alpha"] * np.random.normal()),
            "nn_layers": [
                # tune.grid_search will make it so that all values are evaluated.
                tune.grid_search([16, 64, 256]),
                tune.grid_search([16, 64, 256]),
            ],
        },
    )
    tuner.fit()

> **Tip:** Avoid passing large objects as values in the search space, as that will incur a performance overhead.
Use tune.with_parameters to pass large objects in or load them inside your trainable
from disk (making sure that all nodes have access to the files) or cloud storage.
See tune-bottlenecks for more information.

How to use Custom and Conditional Search Spaces in Tune?

You'll often run into awkward search spaces (i.e., when one hyperparameter depends on another).
Use `tune.sample_from(func)` to provide a **custom** callable function for generating a search space.

The parameter `func` should take in a `config` dict, which contains the values
already sampled for the trial, letting you access other hyperparameters.
This is useful for conditional distributions:

    tuner = tune.Tuner(
        ...,
        param_space={
            # A random function
            "alpha": tune.sample_from(lambda _: np.random.uniform(100)),
            # Use the `config` dict to access other hyperparameters
            "beta": tune.sample_from(lambda config: config["alpha"] * np.random.normal())
        }
    )
    tuner.fit()

Here's an example showing a grid search over two nested parameters combined with random sampling from
two lambda functions, generating 9 different trials.
Note that the value of `beta` depends on the value of `alpha`,
which is represented by referencing `config["alpha"]` in the lambda function.
This lets you specify conditional parameter distributions.

:emphasize-lines: 4-11

    tuner = tune.Tuner(
        my_trainable,
        run_config=RunConfig(name="my_trainable"),
        param_space={
            "alpha": tune.sample_from(lambda _: np.random.uniform(100)),
            "beta": tune.sample_from(lambda config: config["alpha"] * np.random.normal()),
            "nn_layers": [
                tune.grid_search([16, 64, 256]),
                tune.grid_search([16, 64, 256]),
            ],
        }
    )

> **Note:** This format is not supported by every SearchAlgorithm, and only some SearchAlgorithms, like HyperOpt
and Optuna, handle conditional search spaces at all.

    In order to use conditional search spaces with HyperOpt,
    a [Hyperopt search space](http://hyperopt.github.io/hyperopt/getting-started/search_spaces/) isnecessary.
    Optuna supports conditional search spaces through its define-by-run
    interface (/tune/examples/optuna_example).
