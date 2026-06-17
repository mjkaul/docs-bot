---
id: ray-observability.reference.api
title: State API
topic_type: concept
description: ''
subjects:
- observability
mentions: []
references: []
canonical_path: /en/latest/ray-observability/reference/api
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-observability/reference/api.rst
license: Apache 2.0, The Ray Authors
---

State API

> **Note:** APIs are alpha. This feature requires a full installation of Ray using `pip install "ray[default]"`.

For an overview with examples see Monitoring Ray States.

For the CLI reference see Ray State CLI Reference or Ray Log CLI Reference.

State Python SDK

State APIs are also exported as functions.

Summary APIs

   ray.util.state.summarize_actors
   ray.util.state.summarize_objects
   ray.util.state.summarize_tasks

List APIs

    ray.util.state.list_actors
    ray.util.state.list_placement_groups
    ray.util.state.list_nodes
    ray.util.state.list_jobs
    ray.util.state.list_workers
    ray.util.state.list_tasks
    ray.util.state.list_objects
    ray.util.state.list_runtime_envs

Get APIs

    ray.util.state.get_actor
    ray.util.state.get_placement_group
    ray.util.state.get_node
    ray.util.state.get_worker
    ray.util.state.get_task
    ray.util.state.get_objects

Log APIs

    ray.util.state.list_logs
    ray.util.state.get_log

State APIs Schema

    ray.util.state.common.ActorState
    ray.util.state.common.TaskState
    ray.util.state.common.NodeState
    ray.util.state.common.PlacementGroupState
    ray.util.state.common.WorkerState
    ray.util.state.common.ObjectState
    ray.util.state.common.RuntimeEnvState
    ray.util.state.common.JobState
    ray.util.state.common.StateSummary
    ray.util.state.common.TaskSummaries
    ray.util.state.common.TaskSummaryPerFuncOrClassName
    ray.util.state.common.ActorSummaries
    ray.util.state.common.ActorSummaryPerClass
    ray.util.state.common.ObjectSummaries
    ray.util.state.common.ObjectSummaryPerKey

State APIs Exceptions

    ray.util.state.exception.RayStateApiException
