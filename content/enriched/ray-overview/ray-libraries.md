---
id: ray-overview.ray-libraries
title: The Ray Ecosystem
topic_type: section
description: ''
subjects:
- core
- data
- serve
- train
mentions:
- batch-inference
- dataset
- trainer
references: []
canonical_path: /en/latest/ray-overview/ray-libraries
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-overview/ray-libraries.rst
license: Apache 2.0, The Ray Authors
---

The Ray Ecosystem

This page lists libraries that have integrations with Ray for distributed execution
in alphabetical order.
It's easy to add your own integration to this list.
Simply open a pull request with a few lines of text, see the dropdown below for
more information.

    To add an integration add an entry to this file, using the same
    `grid-item-card` directive that the other examples use.

    :gutter: 1
    :class-container: container pb-3

    .. grid-item-card::

        
        .. div::

            
            Agentic-Ray enables agents built with any framework to use Ray as their runtime, distribute tool calls across a cluster, and provision sandbox environments for executing AI-generated code.

        +++
        .. button-link:: https://rayai.com
            :color: primary
            :outline:
            :expand:

            Agentic-Ray Integration

    .. grid-item-card::

        
        .. div::

            
            Apache Airflow® is an open-source platform that enables users to programmatically author, schedule, and monitor workflows using directed acyclic graphs (DAGs). With the Ray provider, users can seamlessly orchestrate Ray jobs within Airflow DAGs.

        +++
        .. button-link:: https://astronomer.github.io/astro-provider-ray/
            :color: primary
            :outline:
            :expand:

            Apache Airflow Integration

    .. grid-item-card::

        
        .. div::

            
            BuildFlow is a backend framework that allows you to build and manage complex cloud infrastructure using pure python. With BuildFlow's decorator pattern you can turn any function into a component of your backend system.

        +++
        .. button-link:: https://docs.launchflow.com/buildflow/introduction
            :color: primary
            :outline:
            :expand:

            BuildFlow Integration

    .. grid-item-card::

        
        .. div::

            
            Classy Vision is a new end-to-end, PyTorch-based framework for large-scale training of state-of-the-art image and video classification models. The library features a modular, flexible design that allows anyone to train machine learning models on top of PyTorch using very simple abstractions.

        +++
        .. button-link:: https://github.com/facebookresearch/ClassyVision/blob/main/tutorials/ray_aws.ipynb
            :color: primary
            :outline:
            :expand:

            Classy Vision Integration

    .. grid-item-card::

        
        .. div::

            
            Daft is a high-performance multimodal data engine that provides simple and reliable data processing for any modality - from structured tables to images, audio, video, and embeddings. Built with Python and Rust for modern AI workflows, Daft offers seamless scaling from local to [distributed clusters](https://www.daft.ai/cloud), enabling efficient batch inference, document processing, and multimodal ETL pipelines at scale.

        +++
        .. button-link:: https://docs.daft.ai/en/stable/distributed/ray/
            :color: primary
            :outline:
            :expand:

            Daft Integration

    .. grid-item-card::

        
        .. div::

            
            Dask provides advanced parallelism for analytics, enabling performance at scale for the tools you love. Dask uses existing Python APIs and data structures to make it easy to switch between Numpy, Pandas, Scikit-learn to their Dask-powered equivalents.

        +++
        .. button-ref:: dask-on-ray
            :color: primary
            :outline:
            :expand:

            Dask Integration

    .. grid-item-card::

        
        .. div::

            
            Data-Juicer is a one-stop multimodal data processing system to make data higher-quality, juicier, and more digestible for foundation models. It integrates with Ray for distributed data processing on large-scale datasets with over 100 multimodal operators and supports TB-size dataset deduplication.

        +++
        .. button-link:: https://github.com/modelscope/data-juicer?tab=readme-ov-file#distributed-data-processing
            :color: primary
            :outline:
            :expand:

            Data-Juicer Integration

    .. grid-item-card::

        
        .. div::

            
            Flambé is a machine learning experimentation framework built to accelerate the entire research life cycle. Flambé’s main objective is to provide a unified interface for prototyping models, running experiments containing complex pipelines, monitoring those experiments in real-time, reporting results, and deploying a final model for inference.

        +++
        .. button-link:: https://github.com/asappresearch/flambe
            :color: primary
            :outline:
            :expand:

            Flambé Integration

    .. grid-item-card::

        
        .. div::

            
            Flowdapt is a platform designed to help developers configure, debug, schedule, trigger, deploy and serve adaptive and reactive Artificial Intelligence workflows at large-scale.

        +++
        .. button-link:: https://github.com/emergentmethods/flowdapt
            :color: primary
            :outline:
            :expand:

            Flowdapt Integration

    .. grid-item-card::

        
        .. div::

            
            Flyte is a Kubernetes-native workflow automation platform for complex, mission-critical data and ML processes at scale. It has been battle-tested at Lyft, Spotify, Freenome, and others and is truly open-source.

        +++
        .. button-link:: https://flyte.org/
            :color: primary
            :outline:
            :expand:

            Flyte Integration

    .. grid-item-card::

        
        .. div::

            
            Horovod is a distributed deep learning training framework for TensorFlow, Keras, PyTorch, and Apache MXNet. The goal of Horovod is to make distributed deep learning fast and easy to use.

        +++
        .. button-link:: https://horovod.readthedocs.io/en/stable/ray_include.html
            :color: primary
            :outline:
            :expand:

            Horovod Integration

    .. grid-item-card::

        
        .. div::

            
            State-of-the-art Natural Language Processing for Pytorch and TensorFlow 2.0. It integrates with Ray for distributed hyperparameter tuning of transformer models.

        +++
        .. button-link:: https://huggingface.co/transformers/master/main_classes/trainer.html#transformers.Trainer.hyperparameter_search
            :color: primary
            :outline:
            :expand:

            Hugging Face Transformers Integration

    .. grid-item-card::

        
        .. div::

            
            Analytics Zoo seamlessly scales TensorFlow, Keras and PyTorch to distributed big data (using Spark, Flink & Ray).

        +++
        .. button-link:: https://analytics-zoo.github.io/master/#ProgrammingGuide/rayonspark/
            :color: primary
            :outline:
            :expand:

            Intel Analytics Zoo Integration

    .. grid-item-card::

        
        .. div::

            
            The power of 350+ pre-trained NLP models, 100+ Word Embeddings, 50+ Sentence Embeddings, and 50+ Classifiers in 46 languages with 1 line of Python code.

        +++
        .. button-link:: https://nlu.johnsnowlabs.com/docs/en/predict_api#modin-dataframe
            :color: primary
            :outline:
            :expand:

            NLU Integration

    .. grid-item-card::

        
        .. div::

            
            Ludwig is a toolbox that allows users to train and test deep learning models without the need to write code. With Ludwig, you can train a deep learning model on Ray in zero lines of code, automatically leveraging Dask on Ray for data preprocessing, Horovod on Ray for distributed training, and Ray Tune for hyperparameter optimization.

        +++
        .. button-link:: https://medium.com/ludwig-ai/ludwig-ai-v0-4-introducing-declarative-mlops-with-ray-dask-tabnet-and-mlflow-integrations-6509c3875c2e
            :color: primary
            :outline:
            :expand:

            Ludwig Integration

    .. grid-item-card::

        
        .. div::

            
            Mars is a tensor-based unified framework for large-scale data computation which scales Numpy, Pandas and Scikit-learn. Mars can scale in to a single machine, and scale out to a cluster with thousands of machines.

        +++
        .. button-ref:: mars-on-ray
            :color: primary
            :outline:
            :expand:

            MARS Integration

    .. grid-item-card::

        
        .. div::

            
            Scale your pandas workflows by changing one line of code. Modin transparently distributes the data and computation so that all you need to do is continue using the pandas API as you were before installing Modin.

        +++
        .. button-link:: https://github.com/modin-project/modin
            :color: primary
            :outline:
            :expand:

            Modin Integration

    .. grid-item-card::

        
        .. div::

            
            Prefect is an open source workflow orchestration platform in Python. It allows you to easily define, track and schedule workflows in Python. This integration makes it easy to run a Prefect workflow on a Ray cluster in a distributed way.

        +++
        .. button-link:: https://github.com/PrefectHQ/prefect-ray
            :color: primary
            :outline:
            :expand:

            Prefect Integration

    .. grid-item-card::

        
        .. div::

            
            PyCaret is an open source low-code machine learning library in Python that aims to reduce the hypothesis to insights cycle time in a ML experiment. It enables data scientists to perform end-to-end experiments quickly and efficiently.

        +++
        .. button-link:: https://github.com/pycaret/pycaret
            :color: primary
            :outline:
            :expand:

            PyCaret Integration

    .. grid-item-card::

        
        .. div::

            
            RayDP ("Spark on Ray") enables you to easily use Spark inside a Ray program. You can use Spark to read the input data, process the data using SQL, Spark DataFrame, or Pandas (via Koalas) API, extract and transform features using Spark MLLib, and use RayDP Estimator API for distributed training on the preprocessed dataset.

        +++
        .. button-link:: https://github.com/Intel-bigdata/oap-raydp
            :color: primary
            :outline:
            :expand:

            RayDP Integration

    .. grid-item-card::

        
        .. div::

            
            Raylight is an extension for ComfyUI that enables true multi-GPU capability using XDiT XFuser, and FSDP managed by Ray. It is designed to scale diffusion models efficiently across multiple GPUs. Raylight provides sequence parallelism, and optimized VRAM utilization, making it ideal for large video and image generation models.

        +++
        .. button-link:: https://github.com/komikndr/raylight
            :color: primary
            :outline:
            :expand:

            Raylight Integration

    .. grid-item-card::

        
        .. div::

            
            Scikit-learn is a free software machine learning library for the Python programming language. It features various classification, regression and clustering algorithms including support vector machines, random forests, gradient boosting, k-means and DBSCAN, and is designed to interoperate with the Python numerical and scientific libraries NumPy and SciPy.

        +++
        .. button-link:: https://docs.ray.io/en/master/joblib.html
            :color: primary
            :outline:
            :expand:

            Scikit Learn Integration

    .. grid-item-card::

        
        .. div::

            
            Alibi is an open source Python library aimed at machine learning model inspection and interpretation. The focus of the library is to provide high-quality implementations of black-box, white-box, local and global explanation methods for classification and regression models.

        +++
        .. button-link:: https://github.com/SeldonIO/alibi
            :color: primary
            :outline:
            :expand:

            Seldon Alibi Integration

    .. grid-item-card::

        
        .. div::

            
            Sematic is an open-source ML pipelining tool written in Python. It enables users to write end-to-end pipelines that can seamlessly transition between your laptop and the cloud, with rich visualizations, traceability, reproducibility, and usability as first-class citizens. This integration enables dynamic allocation of Ray clusters within Sematic pipelines.

        +++
        .. button-link:: https://docs.sematic.dev/integrations/ray
            :color: primary
            :outline:
            :expand:

            Sematic Integration

    .. grid-item-card::

        
        .. div::

            
            spaCy is a library for advanced Natural Language Processing in Python and Cython. It's built on the very latest research, and was designed from day one to be used in real products.

        +++
        .. button-link:: https://pypi.org/project/spacy-ray/
            :color: primary
            :outline:
            :expand:

            spaCy Integration

    .. grid-item-card::

        
        .. div::

            
            XGBoost is a popular gradient boosting library for classification and regression. It is one of the most popular tools in data science and workhorse of many top-performing Kaggle kernels.

        +++
        .. button-link:: https://github.com/ray-project/xgboost_ray
            :color: primary
            :outline:
            :expand:

            XGBoost Integration

    .. grid-item-card::

        
        .. div::

            
            LightGBM is a high-performance gradient boosting library for classification and regression. It is designed to be distributed and efficient.

        +++
        .. button-link:: https://github.com/ray-project/lightgbm_ray
            :color: primary
            :outline:
            :expand:

            LightGBM Integration

    .. grid-item-card::

        
        .. div::

            
            Volcano is system for running high-performance workloads on Kubernetes. It features powerful batch scheduling capabilities required by ML and other data-intensive workloads.

        +++
        .. button-link:: https://github.com/volcano-sh/volcano/releases/tag/v1.7.0
            :color: primary
            :outline:
            :expand:

            Volcano Integration
