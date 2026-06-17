---
id: ray-core.compiled-graph.overlap
title: 'Experimental: Overlapping communication and computation'
topic_type: concept
description: ''
subjects:
- core
mentions:
- compiled-graph
references: []
canonical_path: /en/latest/ray-core/compiled-graph/overlap
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/compiled-graph/overlap.rst
license: Apache 2.0, The Ray Authors
---

Experimental: Overlapping communication and computation

Compiled Graph currently provides experimental support for GPU communication and computation overlap. When you turn this feature on, it automatically overlaps the GPU communication with computation operations, thereby hiding the communication overhead and improving performance.

To enable this feature, specify `_overlap_gpu_communication=True` when calling dag.experimental_compile().

The following code has GPU communication and computation operations that benefit
from overlapping.

The output of the preceding code includes the following two lines:

    overlap_gpu_communication=False, duration=1.0670117866247892
    overlap_gpu_communication=True, duration=0.9211348341777921

The actual performance numbers may vary on different hardware, but enabling `_overlap_gpu_communication` improves latency by about 14% for this example.
