---
id: data.custom-datasource-example
title: 'Advanced: Read and Write Custom File Types'
topic_type: concept
description: ''
subjects:
- data
mentions:
- dataset
- datasource
references: []
canonical_path: /en/latest/data/custom-datasource-example
source: https://github.com/ray-project/ray/blob/master/doc/source/data/custom-datasource-example.rst
license: Apache 2.0, The Ray Authors
---

Advanced: Read and Write Custom File Types

This guide shows you how to extend Ray Data to read and write file types that aren't
natively supported. This is an advanced guide, and you'll use unstable internal APIs.

Images are already supported with the ~ray.data.read_images
and ~ray.data.Dataset.write_images APIs, but this example shows you how to
implement them for illustrative purposes.

Read data from files

> **Tip:** If you're not contributing to Ray Data, you don't need to create a
~ray.data.Datasource. Instead, you can call
~ray.data.read_binary_files and decode files with
~ray.data.Dataset.map.

The core abstraction for reading files is ~ray.data.datasource.FileBasedDatasource.
It provides file-specific functionality on top of the
~ray.data.Datasource interface.

To subclass ~ray.data.datasource.FileBasedDatasource, implement the constructor
and `_read_stream`.

Implement the constructor

Call the superclass constructor and specify the files you want to read.
Optionally, specify valid file extensions. Ray Data ignores files with other extensions.

Implement `_read_stream`

`_read_stream` is a generator that yields one or more blocks of data from a file.

[Blocks](https://github.com/ray-project/ray/blob/23d3bfcb9dd97ea666b7b4b389f29b9cc0810121/python/ray/data/block.py#L54)
are a Data-internal abstraction for a collection of rows. They can be PyArrow tables,
pandas DataFrames, or dictionaries of NumPy arrays.

Don't create a block directly. Instead, add rows of data to a
[DelegatingBlockBuilder](https://github.com/ray-project/ray/blob/23d3bfcb9dd97ea666b7b4b389f29b9cc0810121/python/ray/data/_internal/delegating_block_builder.py#L10).

Read your data

Once you've implemented `ImageDatasource`, call ~ray.data.read_datasource to
read images into a ~ray.data.Dataset. Ray Data reads your files in parallel.

Write data to files

> **Note:** The write interface is under active development and might change in the future. If
you have feature requests,
[open a GitHub Issue](https://github.com/ray-project/ray/issues/new?assignees=&labels=enhancement%2Ctriage&projects=&template=feature-request.yml&title=%5B%3CRay+component%3A+Core%7CRLlib%7Cetc...%3E%5D+).

The core abstractions for writing data to files are ~ray.data.datasource.RowBasedFileDatasink and
~ray.data.datasource.BlockBasedFileDatasink. They provide file-specific functionality on top of the
~ray.data.Datasink interface.

If you want to write one row per file, subclass ~ray.data.datasource.RowBasedFileDatasink.
Otherwise, subclass ~ray.data.datasource.BlockBasedFileDatasink.

In this example, you'll write one image per file, so you'll subclass
~ray.data.datasource.RowBasedFileDatasink. To subclass
~ray.data.datasource.RowBasedFileDatasink, implement the constructor and
~ray.data.datasource.RowBasedFileDatasink.write_row_to_file.

Implement the constructor

Call the superclass constructor and specify the folder to write to. Optionally, specify
a string representing the file format (for example, `"png"`). Ray Data uses the
file format as the file extension.

Implement `write_row_to_file`

`write_row_to_file` writes a row of data to a file. Each row is a dictionary that maps
column names to values.

Write your data

Once you've implemented `ImageDatasink`, call ~ray.data.Dataset.write_datasink
to write images to files. Ray Data writes to multiple files in parallel.
