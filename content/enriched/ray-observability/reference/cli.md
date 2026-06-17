---
id: ray-observability.reference.cli
title: State CLI
topic_type: concept
description: ''
subjects:
- observability
- core
mentions:
- actor
- task
references: []
canonical_path: /en/latest/ray-observability/reference/cli
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-observability/reference/cli.rst
license: Apache 2.0, The Ray Authors
---

State CLI

State

This section contains commands to access the live state of Ray resources (actor, task, object, etc.).

> **Note:** APIs are alpha. This feature requires a full installation of Ray using `pip install "ray[default]"`. This feature also requires the dashboard component to be available. The dashboard component needs to be included when starting the ray cluster, which is the default behavior for `ray start` and `ray.init()`. For more in-depth debugging, you could check the dashboard log at `<RAY_LOG_DIR>/dashboard.log`, which is usually `/tmp/ray/session_latest/logs/dashboard.log`.

State CLI allows users to access the state of various resources (e.g., actor, task, object).

   :prog: ray summary tasks

   :prog: ray summary actors

   :prog: ray summary objects

   :prog: ray list

   :prog: ray get

Log

This section contains commands to access logs from Ray clusters.

> **Note:** APIs are alpha. This feature requires a full installation of Ray using `pip install "ray[default]"`.

Log CLI allows users to access the log from the cluster.
Note that only the logs from alive nodes are available through this API.

   :prog: ray logs
