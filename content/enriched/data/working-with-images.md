---
id: data.working-with-images
title: Working with Images
topic_type: task
description: ''
subjects:
- data
- serve
mentions:
- batch-inference
- dataset
references: []
canonical_path: /en/latest/data/working-with-images
source: https://github.com/ray-project/ray/blob/master/doc/source/data/working-with-images.rst
license: Apache 2.0, The Ray Authors
---

Working with Images

With Ray Data, you can easily read and transform large image datasets.

This guide shows you how to:

* Read images
* Transform images
* Perform inference on images
* Save images

Reading images

Ray Data can read images from a variety of formats.

To view the full list of supported file formats, see the
Loading Data API.

    
        To load raw images like JPEG files, call ~ray.data.read_images.  In the schema, the column name defaults to "image".

        
> **Note:** ~ray.data.read_images uses
[PIL](https://pillow.readthedocs.io/en/stable/index.html). For a list of
supported file formats, see
[Image file formats](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html).

        
            import ray

            ds = ray.data.read_images("s3://anonymous@ray-example-data/batoidea/JPEGImages")

            print(ds.schema())

        
            Column  Type
            ------  ----
            image   ArrowTensorTypeV2(shape=(32, 32, 3), dtype=uint8)

    
        To load images from a dataset of URIs, use the ~ray.data.Dataset.with_column method together with the ~ray.data.expressions.download expression.

        
            import pyarrow.fs

            import ray
            from ray.data.expressions import download

            ds = ray.data.read_parquet("s3://anonymous@ray-example-data/imagenet/metadata_file.parquet")
            ds = ds.with_column(
                "bytes",
                download(
                    "image_url",
                    filesystem=pyarrow.fs.S3FileSystem(anonymous=True, region="us-west-2"),
                ),
            )

            print(ds.schema())

        
            Column     Type
            ------     ----
            image_url  string
            bytes      binary

    
        To load images stored in NumPy format, call ~ray.data.read_numpy.

        
            import ray

            ds = ray.data.read_numpy("s3://anonymous@air-example-data/cifar-10/images.npy")

            print(ds.schema())

        
            Column  Type
            ------  ----
            data    ArrowTensorTypeV2(shape=(32, 32, 3), dtype=uint8)

    
        Image datasets often contain `tf.train.Example` messages that look like this:

        
            features {
                feature {
                    key: "image"
                    value {
                        bytes_list {
                            value: ...  # Raw image bytes
                        }
                    }
                }
                feature {
                    key: "label"
                    value {
                        int64_list {
                            value: 3
                        }
                    }
                }
            }

        To load examples stored in this format, call ~ray.data.read_tfrecords.
        Then, call ~ray.data.Dataset.map to decode the raw image bytes.

        
            import io
            from typing import Any, Dict
            import numpy as np
            from PIL import Image
            import ray

            def decode_bytes(row: Dict[str, Any]) -> Dict[str, Any]:
                data = row["image"]
                image = Image.open(io.BytesIO(data))
                row["image"] = np.asarray(image)
                return row

            ds = (
                ray.data.read_tfrecords(
                    "s3://anonymous@air-example-data/cifar-10/tfrecords"
                )
                .map(decode_bytes)
            )

            print(ds.schema())

        ..
            The following `testoutput` is mocked because the order of column names can
            be non-deterministic. For an example, see
            https://buildkite.com/ray-project/oss-ci-build-branch/builds/4849#01892c8b-0cd0-4432-bc9f-9f86fcd38edd.

        
            Column  Type
            ------  ----
            image   ArrowTensorTypeV2(shape=(32, 32, 3), dtype=uint8)
            label   int64

    
        To load image data stored in Parquet files, call ray.data.read_parquet.

        
            import ray

            ds = ray.data.read_parquet("s3://anonymous@air-example-data/cifar-10/parquet")

            print(ds.schema())

        
            Column  Type
            ------  ----
            img     struct<bytes: binary, path: string>
            label   int64

For more information on creating datasets, see Loading Data.

Transforming images

To transform images, call ~ray.data.Dataset.map or
~ray.data.Dataset.map_batches.

    from typing import Any, Dict
    import numpy as np
    import ray

    def increase_brightness(batch: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        batch["image"] = np.clip(batch["image"] + 4, 0, 255)
        return batch

    ds = (
        ray.data.read_images("s3://anonymous@ray-example-data/batoidea/JPEGImages")
        .map_batches(increase_brightness, batch_size="auto")
    )

For more information on transforming data, see
Transforming data.

Performing inference on images

To perform inference with a pre-trained model, first load and transform your data.

    from typing import Any, Dict
    from torchvision import transforms
    import ray

    def transform_image(row: Dict[str, Any]) -> Dict[str, Any]:
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Resize((32, 32))
        ])
        row["image"] = transform(row["image"])
        return row

    ds = (
        ray.data.read_images("s3://anonymous@ray-example-data/batoidea/JPEGImages")
        .map(transform_image)
    )

Next, implement a callable class that sets up and invokes your model.

    import torch
    from torchvision import models

    class ImageClassifier:
        def __init__(self):
            weights = models.ResNet18_Weights.DEFAULT
            self.model = models.resnet18(weights=weights)
            self.model.eval()

        def __call__(self, batch):
            inputs = torch.from_numpy(batch["image"])
            with torch.inference_mode():
                outputs = self.model(inputs)
            return {"class": outputs.argmax(dim=1)}

Finally, call Dataset.map_batches().

    predictions = ds.map_batches(
        ImageClassifier,
        compute=ray.data.ActorPoolStrategy(size=2),
        batch_size=4
    )
    predictions.show(3)

    {'class': 118}
    {'class': 153}
    {'class': 296}

For more information on performing inference, see
End-to-end: Offline Batch Inference
and Stateful Transforms.

Saving images

Save images with formats like PNG, Parquet, and NumPy. To view all supported formats,
see the Saving Data API.

    
        To save images as image files, call ~ray.data.Dataset.write_images.

        
            import ray

            ds = ray.data.read_images("s3://anonymous@ray-example-data/image-datasets/simple")
            ds.write_images("/tmp/simple", column="image", file_format="png")

    
        To save images in Parquet files, call ~ray.data.Dataset.write_parquet.

        
            import ray

            ds = ray.data.read_images("s3://anonymous@ray-example-data/image-datasets/simple")
            ds.write_parquet("/tmp/simple")

    
        To save images in a NumPy file, call ~ray.data.Dataset.write_numpy.

        
            import ray

            ds = ray.data.read_images("s3://anonymous@ray-example-data/image-datasets/simple")
            ds.write_numpy("/tmp/simple", column="image")

For more information on saving data, see Saving data.
