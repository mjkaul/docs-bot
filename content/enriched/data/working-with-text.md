---
id: data.working-with-text
title: Working with Text
topic_type: task
description: ''
subjects:
- data
- serve
mentions:
- batch-inference
- dataset
references: []
canonical_path: /en/latest/data/working-with-text
source: https://github.com/ray-project/ray/blob/master/doc/source/data/working-with-text.rst
license: Apache 2.0, The Ray Authors
---

Working with Text

With Ray Data, you can easily read and transform large amounts of text data.

This guide shows you how to:

* Read text files
* Transform text data
* Perform inference on text data
* Save text data

Reading text files

Ray Data can read lines of text and JSONL. Alternatively, you can read raw binary
files and manually decode data.

    
        To read lines of text, call ~ray.data.read_text. Ray Data creates a
        row for each line of text. In the schema, the column name defaults to "text". 

        
            import ray

            ds = ray.data.read_text("s3://anonymous@ray-example-data/this.txt")

            ds.show(3)

        
            {'text': 'The Zen of Python, by Tim Peters'}
            {'text': 'Beautiful is better than ugly.'}
            {'text': 'Explicit is better than implicit.'}

    
        [JSON Lines](https://jsonlines.org/) is a text format for structured data.
        It's typically used to process data one record at a time.

        To read JSON Lines files, call ~ray.data.read_json. Ray Data creates a
        row for each JSON object.

        
            import ray

            ds = ray.data.read_json("s3://anonymous@ray-example-data/logs.json")

            ds.show(3)

        
            {'timestamp': datetime.datetime(2022, 2, 8, 15, 43, 41), 'size': 48261360}
            {'timestamp': datetime.datetime(2011, 12, 29, 0, 19, 10), 'size': 519523}
            {'timestamp': datetime.datetime(2028, 9, 9, 5, 6, 7), 'size': 2163626}

    
        To read other text formats, call ~ray.data.read_binary_files. Then,
        call ~ray.data.Dataset.map to decode your data.

        
            from typing import Any, Dict
            from bs4 import BeautifulSoup
            import ray

            def parse_html(row: Dict[str, Any]) -> Dict[str, Any]:
                html = row["bytes"].decode("utf-8")
                soup = BeautifulSoup(html, features="html.parser")
                return {"text": soup.get_text().strip()}

            ds = (
                ray.data.read_binary_files("s3://anonymous@ray-example-data/index.html")
                .map(parse_html)
            )

            ds.show()

        
            {'text': 'Batoidea\nBatoidea is a superorder of cartilaginous fishes...'}

For more information on reading files, see Loading data.

Transforming text

To transform text, implement your transformation in a function or callable class. Then,
call Dataset.map() or
Dataset.map_batches(). Ray Data transforms your
text in parallel.

    from typing import Any, Dict
    import ray

    def to_lower(row: Dict[str, Any]) -> Dict[str, Any]:
        row["text"] = row["text"].lower()
        return row

    ds = (
        ray.data.read_text("s3://anonymous@ray-example-data/this.txt")
        .map(to_lower)
    )

    ds.show(3)

    {'text': 'the zen of python, by tim peters'}
    {'text': 'beautiful is better than ugly.'}
    {'text': 'explicit is better than implicit.'}

For more information on transforming data, see
Transforming data.

Performing inference on text

To perform inference with a pre-trained model on text data, implement a callable class
that sets up and invokes a model. Then, call
Dataset.map_batches().

    from typing import Dict

    import numpy as np
    from transformers import pipeline

    import ray

    class TextClassifier:
        def __init__(self):

            self.model = pipeline("text-classification")

        def __call__(self, batch: Dict[str, np.ndarray]) -> Dict[str, list]:
            predictions = self.model(list(batch["text"]))
            batch["label"] = [prediction["label"] for prediction in predictions]
            return batch

    ds = (
        ray.data.read_text("s3://anonymous@ray-example-data/this.txt")
        .map_batches(TextClassifier, compute=ray.data.ActorPoolStrategy(size=2), batch_size="auto")
    )

    ds.show(3)

    {'text': 'The Zen of Python, by Tim Peters', 'label': 'POSITIVE'}
    {'text': 'Beautiful is better than ugly.', 'label': 'POSITIVE'}
    {'text': 'Explicit is better than implicit.', 'label': 'POSITIVE'}

For more information on handling large language models, see Working with LLMs.

For more information on performing inference, see
End-to-end: Offline Batch Inference
and Stateful Transforms.

Saving text

To save text, call a method like ~ray.data.Dataset.write_parquet. Ray Data can
save text in many formats.

To view the full list of supported file formats, see the
Saving Data API.

    import ray

    ds = ray.data.read_text("s3://anonymous@ray-example-data/this.txt")

    ds.write_parquet("local:///tmp/results")

For more information on saving data, see Saving data.
