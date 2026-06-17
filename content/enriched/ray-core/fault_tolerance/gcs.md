---
id: ray-core.fault_tolerance.gcs
title: GCS Fault Tolerance
topic_type: concept
description: ''
subjects:
- core
mentions:
- actor
- head-node
- placement-group
- task
- worker
references: []
canonical_path: /en/latest/ray-core/fault_tolerance/gcs
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/fault_tolerance/gcs.rst
license: Apache 2.0, The Ray Authors
---

GCS Fault Tolerance

The Global Control Service, or GCS, manages cluster-level metadata.
It also provides a handful of cluster-level operations including actor, placement groups and node management.
By default, the GCS isn't fault tolerant because it stores all data in memory. If it fails, the entire Ray cluster fails.
To enable GCS fault tolerance, you need a highly available Redis instance, known as HA Redis.
Then, when the GCS restarts, it loads all the data from the Redis instance and resumes regular functions.

During the recovery period, the following functions aren't available:

- Actor creation, deletion and reconstruction.
- Placement group creation, deletion and reconstruction.
- Resource management.
- Worker node registration.
- Worker process creation.

However, running Ray tasks and actors remain alive, and any existing objects stay available.

Setting up Redis

        If you are using KubeRay, refer to KubeRay docs on GCS Fault Tolerance.

    
        If you are using ray start to start the Ray head node,
        set the OS environment `RAY_REDIS_ADDRESS` to
        the Redis address, and supply the `--redis-password` flag with the password when calling `ray start`:

        
          RAY_REDIS_ADDRESS=redis_ip:port ray start --head --redis-password PASSWORD --redis-username default

    
        If you are using ray up to start the Ray cluster, change head_start_ray_commands field to add `RAY_REDIS_ADDRESS` and `--redis-password` to the `ray start` command:

        
          head_start_ray_commands:
            - ray stop
            - ulimit -n 65536; RAY_REDIS_ADDRESS=redis_ip:port ray start --head --redis-password PASSWORD --redis-username default --port=6379 --object-manager-port=8076 --autoscaling-config=~/ray_bootstrap_config.yaml --dashboard-host=0.0.0.0

After you back the GCS with Redis, it recovers its state from Redis when it restarts.
While the GCS recovers, each raylet tries to reconnect to it.
If a raylet can't reconnect for more than 60 seconds, that raylet exits and the corresponding node fails.
Set this timeout threshold with the OS environment variable `RAY_gcs_rpc_server_reconnect_timeout_s`.

If the GCS IP address might change after restarts, use a qualified domain name
and pass it to all raylets at start time. Each raylet resolves the domain name and connects to
the correct GCS. You need to ensure that at any time, only one GCS is alive.

> **Note:** GCS fault tolerance with external Redis is officially supported
only if you are using KubeRay for Ray serve fault tolerance.
For other cases, you can use it at your own risk and
you need to implement additional mechanisms to detect the failure of GCS or the head node
and restart it.

> **Note:** You can also enable GCS fault tolerance when running Ray on [Anyscale](https://www.anyscale.com/). See the Anyscale [documentation](https://docs.anyscale.com/platform/services/head-node-ft/) for instructions.
