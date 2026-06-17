---
id: data.working-with-llms
title: Working with LLMs
topic_type: task
description: ''
subjects:
- data
- core
- serve
- train
- tune
mentions:
- actor
- batch-inference
- checkpoint
- dataset
- deployment
- placement-group
- replica
- runtime-env
- task
- worker
references: []
canonical_path: /en/latest/data/working-with-llms
source: https://github.com/ray-project/ray/blob/master/doc/source/data/working-with-llms.rst
license: Apache 2.0, The Ray Authors
---

Working with LLMs

The ray.data.llm module enables scalable batch inference on Ray Data datasets. It supports two modes: running LLM inference engines directly (vLLM, SGLang) or querying hosted endpoints through ~ray.data.llm.ServeDeploymentProcessorConfig.

**Getting started:**

* Quickstart - Run your first batch inference job
* Architecture - Understand the processor pipeline
* Scaling - Scale your LLM stage to multiple replicas

**Common use cases:**

* Text generation - Chat completions with LLMs
* Embeddings - Generate text embeddings
* Classification - Content classifiers and sentiment analyzers
* Multimodality - Batch inference with VLM / omni models on multimodal data
* OpenAI-compatible endpoints - Query deployed models
* Serve deployments - Share vLLM engines across processors
* Custom tokenizers - Use vLLM tokenizers for models not supported by HuggingFace

**Operations:**

* Troubleshooting - GPU memory, model loading issues
* Advanced configuration - Parallelism, per-stage tuning, LoRA, batch concurrency

Quickstart: vLLM batch inference

Get started with vLLM batch inference in just a few steps. This example shows the minimal setup needed to run batch inference on a dataset.

> **Note:** This quickstart requires a GPU as vLLM is GPU-accelerated.

First, install Ray Data with LLM support:

    pip install -U "ray[data, llm]>=2.53.0"

Here's a complete minimal example that runs batch inference:

This example:

1. Creates a simple dataset with prompts
2. Configures a vLLM processor with minimal settings
3. Builds a processor that handles preprocessing (converting prompts to OpenAI chat format) and postprocessing (extracting generated text)
4. Runs inference on the dataset
5. Iterates through results

The processor expects input rows with a `prompt` field and outputs rows with both `prompt` and `response` fields. You can consume results using `iter_rows()`, `take()`, `show()`, or save to files with `write_parquet()`.

For more configuration options and advanced features, see the sections below.

Processor architecture

Ray Data LLM uses a **multi-stage processor pipeline** to transform your data through LLM inference. Understanding this architecture helps you optimize performance and debug issues.

    Input Dataset
         |
         v
    - Preprocess (Custom Function)
    - PrepareMultimodal (Optional, for VLM / Omni models)
    - ChatTemplate (Applies chat template to messages)
    - Tokenize (Optional -- converts text to token IDs)
    - LLM Engine (vLLM/SGLang inference on GPU)
    - Detokenize (Optional -- converts token IDs back to text)
    - Postprocess (Custom Function)
         |
         v
    Output Dataset

**Stage descriptions:**

- **Preprocess**: Your custom function that transforms input rows into the format expected by downstream stages (typically OpenAI chat format with `messages`).
- **PrepareMultimodal**: Extracts and prepares multimodal inputs. Enable with `prepare_multimodal_stage=True`.
- **ChatTemplate**: Applies the model's chat template to convert messages into a prompt string.
- **Tokenize**: Converts the prompt string into token IDs for the model.
- **LLM Engine**: The accelerated (GPU/TPU) inference stage running vLLM or SGLang.
- **Detokenize**: Converts output token IDs back to readable text.
- **Postprocess**: Your custom function that extracts and formats the final output.

Each stage runs as a separate Ray actor pool, enabling independent scaling and resource allocation. All stages (CPU and GPU) use autoscaling actor pools by default, except for the ServeDeployment stage which uses a fixed pool.

Scaling to multiple GPUs

Horizontally scale the LLM stage to multiple GPU replicas using the `concurrency` parameter:

Each replica runs an independent inference engine. Set `concurrency` to match the number of available GPUs or GPU nodes.

By default, when you set `concurrency` to an integer `n`, GPU stages autoscale from 1 to `n` actors. To use a fixed pool of `n` actors, set `concurrency` to `(n, n)`.

Text generation

Use vLLMEngineProcessorConfig or SGLangEngineProcessorConfig for chat completions and text generation tasks.

**Key configuration options:**

- `model_source`: HuggingFace model ID or path to model weights
- `concurrency`: Number of vLLM engine replicas (typically 1 per GPU node)
- `batch_size`: Rows per batch (reduce if hitting memory limits)

For gated models requiring authentication, pass your HuggingFace token through `runtime_env`:

Multimodality

Ray Data LLM also supports running batch inference with vision language
and omni-modal models on multimodal data. To enable multimodal batch inference,
apply the following 2 adjustments on top of the previous example:

- Set `prepare_multimodal_stage=True` in the `vLLMEngineProcessorConfig`
- Prepare multimodal data inside the preprocessor.

Image batch inference with vision language model (VLM)

First, load a vision dataset:

Next, configure the VLM processor with the essential settings:

Define preprocessing and postprocessing functions to convert dataset rows into
the format expected by the VLM and extract model responses. Within the preprocessor,
structure image data as part of an OpenAI-compatible message. Both image URL and
`PIL.Image.Image` object are supported.

Finally, run the VLM inference:

Video batch inference with vision language model (VLM)

First, load a video dataset:

Next, configure the VLM processor with the essential settings:

Ray Data LLM forwards `mm_processor_kwargs` to vLLM, which invokes
the model's HuggingFace processor with it. The accepted keys are
defined by the HF processor and differ by model family, for example
`max_pixels` on Qwen2-VL, `size` on Qwen3-VL. Refer to the HF
processor source for your model, for example [Qwen3VLVideoProcessor](https://github.com/huggingface/transformers/blob/10555512868d663ee1ff627e4f5c5c260114235b/src/transformers/models/qwen3_vl/video_processing_qwen3_vl.py#L86).

> **Note:** Understanding multimodal arguments:

   - `engine_kwargs.limit_mm_per_prompt={"video": 1}`: caps the number of videos per request.
   - `engine_kwargs.mm_processor_kwargs.size`: per-frame resize budget;
     inputs are resized to fall within the range
     `shortest_edge` to `longest_edge` in total pixels.
   - `engine_kwargs.mm_processor_kwargs.do_sample_frames=False`: skip the
     HF processor's own frame sampling because `media_io_kwargs` already
     produced the final frames. Set this whenever frame sampling has
     already happened upstream.
   - `prepare_multimodal_stage.model_config_kwargs.allowed_local_media_path`:
     required for `file://` or local-path media inputs.
   - `prepare_multimodal_stage.model_config_kwargs.media_io_kwargs`:
     frame sampling at decode time.

> **Warning:** If a multimodal input exceeds `mm_processor_kwargs.size`, the HF
processor's [smart_resize](https://github.com/huggingface/transformers/blob/10555512868d663ee1ff627e4f5c5c260114235b/src/transformers/models/qwen3_vl/video_processing_qwen3_vl.py#L35)
downscales it automatically. Size `size.longest_edge`
to the largest input you expect to process: `height * width` for an
image, `num_frames * height * width` for a video.

Define preprocessing and postprocessing functions to convert dataset rows into
the format expected by the VLM and extract model responses. Within the preprocessor,
structure video data as part of an OpenAI-compatible message.

Finally, run the VLM inference:

Audio batch inference with omni-modal model

First, load an audio dataset:

Next, configure the omni-modal processor with the essential settings:

Define preprocessing and postprocessing functions to convert dataset rows into
the format expected by the omni-modal model and extract model responses. Within the preprocessor,
structure audio data as part of an OpenAI-compatible message. Both audio URL and audio
binary data are supported.

Finally, run the omni-modal inference:

Embeddings

For embedding models, set `task_type="embed"` and disable chat templating:

Key differences from text generation:

- Use `prompt` input instead of `messages`
- Access results through `row["embeddings"]`

Classification

Ray Data LLM supports batch inference with sequence classification models, such as content classifiers and sentiment analyzers:

Key differences for classification models:

- Set `task_type="classify"` (or `task_type="score"` for scoring models)
- Set `chat_template_stage=False` and `detokenize_stage=False`
- Use direct `prompt` input instead of `messages`
- Access classification logits through `row["embeddings"]`

OpenAI-compatible endpoints

Query deployed models with an OpenAI-compatible API:

Tokenization disaggregation

By default, tokenization and detokenization run as **separate CPU stages** in the processor pipeline. This offloads tokenizer work from the GPU stage, allowing independent scaling of CPU and GPU stages.

> **Note:** When the detokenize stage is enabled, set `detokenize=False` in `sampling_params` so the engine returns raw token IDs for the CPU stage to decode. When disabled, set `detokenize=True` so the engine decodes the output itself.

**Disaggregated (default)**: tokenize and detokenize as separate CPU stages:

Alternatively, you can disable these stages so the vLLM engine handles tokenization and detokenization internally.

**Aggregated**: the vLLM engine handles tokenization internally:

> **Tip:** Disaggregated tokenization is most beneficial when the tokenizer is a bottleneck, for example, with large vocabularies or long sequences.
If the GPU engine is already saturated, the overhead of extra stages may not help.

Custom tokenizers

Use this pattern when a model is supported by vLLM but not by HuggingFace `transformers` — for example, Mistral Tekken (`mistral`), DeepSeek-V3 (`deepseek_v32`), or Grok-2 (`grok2`).
The built-in ChatTemplate, Tokenize, and Detokenize stages rely on HuggingFace and will fail for these models. In the following example, we disable the built-in CPU stages and replace them with `map_batches` callables.

**Chat template**: Converts OpenAI-format messages into the prompt string the model expects. Required because each model family defines its own chat format:

**Tokenize**: Converts the prompt string into token IDs for the model.

**Detokenize** (optional): Decodes generated token IDs back to text. The vLLM engine already returns `generated_text`, so this is only needed for custom decoding (e.g. different `skip_special_tokens` settings):

Build a processor with built-in stages disabled and compose the full pipeline:

> **Note:** This example uses a standard model because models that truly require vLLM's custom tokenizer are too large for Ray CI environments. The pattern is identical — just replace `MODEL_ID` and set `tokenizer_mode` explicitly.

Resiliency

Row-level fault tolerance

In Ray Data LLM, row-level fault tolerance is achieved by setting the `should_continue_on_error` parameter to `True` in the processor config.
This means that if a single row fails due to a request level error from the engine, the job continues processing the remaining rows.
This is useful for long-running jobs where you want to minimize the impact of request failures.

Actor-level fault tolerance

When an actor dies in the middle of a pipeline execution, it's restarted and rejoins the actor pool to process remaining rows.
This feature is enabled by default, and there are no additional configuration needed.

Checkpoint recovery

Ray Data supports checkpoint recovery, which lets you resume pipeline execution from a checkpoint stored in local or cloud storage.
Checkpointing works only for pipelines that start with a read operation and end with a write operation.
For checkpointing to take effect, successful blocks must reach the write sink before a failure occurs. After a failure, you can resume processing from the checkpoint in a subsequent run.

First, set up the checkpoint configuration and specify the ID column for checkpointing.

Then, include a read and write operation in the pipeline to enable checkpoint recovery. It's important to preserve the ID column during postprocess to ensure that the ID column is stored in the checkpoint.

To resume from a checkpoint, run the same code again. Ray Data discovers the checkpoint and resumes from the last successful block.

Advanced configuration

Model parallelism

For large models that don't fit on a single GPU, use tensor and pipeline parallelism:

Cross-node parallelism

Ray Data LLM supports cross-node parallelism, including tensor parallelism and pipeline parallelism. Configure the parallelism level through `engine_kwargs`. The `distributed_executor_backend` defaults to `"ray"` for cross-node support.

You can customize the placement group configuration to control how Ray places vLLM engine workers across nodes. Use `bundle_per_worker` for basic per-worker resource specification (auto-replicated based on TP*PP), or `bundles` for full control over individual bundles. While you can specify the degree of tensor and pipeline parallelism, the specific assignment of model ranks to GPUs is managed by the vLLM engine.

> **Note:** In each bundle dict, omitted `CPU` or `GPU` keys are treated as **0**. Specify the resources each worker needs explicitly.

Per-stage configuration

Configure individual pipeline stages for fine-grained resource control:

    config = vLLMEngineProcessorConfig(
        model_source="meta-llama/Llama-3.1-8B-Instruct",
        chat_template_stage={
            "enabled": True,
            "batch_size": 256,
            "concurrency": 4,
        },
        tokenize_stage={
            "enabled": True,
            "batch_size": 512,
            "num_cpus": 0.5,
        },
        detokenize_stage={
            "enabled": True,
            "concurrency": (2, 8),  # Autoscaling pool
        },
    )

See stage config classes for all available fields.

LoRA adapters

For multi-LoRA batch inference:

See the vLLM with LoRA example for details.

Accelerated model loading with RunAI streamer

Use [RunAI Model Streamer](https://github.com/run-ai/runai-model-streamer) for faster model loading from cloud storage:

> **Note:** Install vLLM with runai dependencies: `pip install -U "vllm[runai]>=0.10.1"`

Tuning concurrent batch processing

Two parameters control concurrent batch processing: `max_concurrent_batches` and `max_tasks_in_flight_per_actor`. Understanding their interaction helps achieve optimal throughput.

Understanding the parameters

`max_concurrent_batches`, default: 8
    The number of batches that can execute concurrently within a single vLLM engine actor. This overlaps batch processing to hide tail latency. The optimal batch size depends on the workload.

`max_tasks_in_flight_per_actor`, experimental, default: 16
    The number of tasks Ray Data can queue per actor before waiting for results. This enables task prefetching so tasks are ready when the actor finishes processing.

How they work together

These parameters control different parts of the pipeline:

- `max_tasks_in_flight_per_actor` controls how many tasks Ray Data sends to the actor queue
- `max_concurrent_batches` controls how many batches can execute simultaneously

With `max_tasks_in_flight_per_actor[ ]( `max_concurrent_batches`, Ray Data actors are undersaturated. To maximize throughput, increase `max_tasks_in_flight_per_actor` to keep the actor task queue saturated.

Serve deployments

For multi-turn conversations or complex agentic workflows, share a vLLM engine across multiple processors using Ray Serve:

Troubleshooting

vLLM compatibility

Each Ray release is fully tested with a compatible vLLM version.

   :header-rows: 1
   :widths: auto

   * - Ray release
     - vLLM version
   * - nightly
     - 0.23.0
   * - 2.56.0
     - 0.22.0
   * - 2.55.0
     - 0.18.0
   * - 2.54.0
     - 0.15.0
   * - 2.53.0
     - 0.12.0
   * - 2.52.0
     - 0.11.0
   * - 2.51.0
     - 0.11.0
   * - 2.50.0
     - 0.10.2

GPU memory and CUDA OOM

If you encounter CUDA out of memory errors, try these strategies:

- Reduce batch size: Start with 8-16 and increase gradually
- Lower `max_num_batched_tokens`: Reduce from 4096 to 2048 or 1024
- Decrease `max_model_len`: Use shorter context lengths
- Set `gpu_memory_utilization`: Use 0.75-0.85 instead of default 0.90

Model loading at scale

For large clusters, HuggingFace downloads may be rate-limited. Cache models to S3 or GCS:

    python -m ray.llm.utils.upload_model \
        --model-source facebook/opt-350m \
        --bucket-uri gs://my-bucket/path/to/model

Then reference the remote path in your config:

vLLM NIXL EP dependency incompatibility

   Users who install Ray and vLLM directly may encounter NIXL EP incompatibility error as follows:

   
      ImportError: libcudart.so.12: cannot open shared object file: No such file or directory

   Remove the incompatible package or ensure the installed `nixl_ep` package is compatible with the CUDA runtime
   and vLLM build in your environment.

**Usage data collection**: Ray collects anonymous usage data to improve Ray Data LLM. To opt out, see Ray usage stats.

Get Help

If you encounter issues not covered in this guide:

- `Ray GitHub Issues <https://github.com/ray-project/ray/issues) - Report bugs or request features
- [Ray Slack](https://ray-distributed.slack.com) - Get help from the community
- [Ray Discourse Forum](https://discuss.ray.io) - Ask questions and share knowledge
- [Ray LLM Office Hours](https://zoom-lfx.platform.linuxfoundation.org/meetings/ray?view=month) - Learn about new features, ask questions, and get guidance from the team

  - [Past Office Hours Recordings](https://youtube.com/playlist?list=PLzTswPQNepXl2IYF8DcV35FdCoVbeL4_6&si=ik81bljIlasYAHKN) - View recordings from previous sessions
