---
id: data.benchmark
title: Ray Data Benchmarks
topic_type: concept
description: ''
subjects:
- data
- serve
mentions:
- batch-inference
- dataset
references: []
canonical_path: /en/latest/data/benchmark
source: https://github.com/ray-project/ray/blob/master/doc/source/data/benchmark.md
license: Apache 2.0, The Ray Authors
---

# Ray Data Benchmarks

This page documents benchmark results and methodologies for evaluating Ray Data performance across a variety of data modalities and workloads.

---

## Workload Summary

- **Image Classification**: Processing 800k ImageNet images using ResNet18. The pipeline downloads images, deserializes them, applies transformations, runs ResNet18 inference on GPU, and outputs predicted labels.
- **Document Embedding**: Processing 10k PDF documents from Digital Corpora. The pipeline reads PDF documents, extracts text page-by-page, splits into chunks with overlap, embeds using a `all-MiniLM-L6-v2` model on GPU, and outputs embeddings with metadata.
- **Audio Transcription**: Transcribing 113,800 audio files from Mozilla Common Voice 17 dataset using a Whisper-tiny model. The pipeline loads FLAC audio files, resamples to 16kHz, extracts features using Whisper's processor, runs GPU-accelerated batch inference with the model, and outputs transcriptions with metadata.
- **Video Object Detection**: Processing 10k video frames from Hollywood2 action videos dataset using YOLOv11n for object detection. The pipeline loads video frames, resizes them to 640x640, runs batch inference with YOLO to detect objects, extracts individual object crops, and outputs object metadata and cropped images in Parquet format.
- **Large-scale Image Embedding**: Processing 4TiB of base64-encoded images from a Parquet dataset using ViT for image embedding. The pipeline decodes base64 images, converts to RGB, preprocesses using ViTImageProcessor (resizing, normalization), runs GPU-accelerated batch inference with ViT to generate embeddings, and outputs results to Parquet format.

Ray Data 2.50 is compared with Daft 0.6.2, an open source multimodal data processing library built on Ray.

---

## Results Summary

![Multimodal Inference Benchmark Results](/data/images/multimodal_inference_results.png)

[code example]

All benchmark results are taken from an average/std across 4 runs. A warmup was also run to download the model and remove any startup overheads that would affect the result.

## Workload Configuration

[code example]

## Image Classification across different instance types

This experiment compares the performance of Ray Data with Daft on the image classification workload across a variety of instance types. Each run is an average/std across 3 runs. A warmup was also run to download the model and remove any startup overheads that would affect the result.

[code example]

## Video Object Detection across different instance types

This experiment compares the performance of Ray Data with Daft on the video object detection workload across a variety of instance types. Each run is an average/std across 4 runs. A warmup was also run to download the model and remove any startup overheads that would affect the result.

[code example]
