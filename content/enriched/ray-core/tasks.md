---
id: ray-core.tasks
title: Tasks
topic_type: concept
description: ''
subjects:
- core
mentions:
- object-ref
- task
- worker
references: []
canonical_path: /en/latest/ray-core/tasks
source: https://github.com/ray-project/ray/blob/master/doc/source/ray-core/tasks.rst
license: Apache 2.0, The Ray Authors
---

Tasks

Ray enables arbitrary functions to be executed asynchronously on separate worker processes. Such functions are called **Ray remote functions** and their asynchronous invocations are called **Ray tasks**. Here is an example.

    
        
        See the ray.remote API for more details.

    
        
          public class MyRayApp {
            // A regular Java static method.
            public static int myFunction() {
              return 1;
            }
          }

          // Invoke the above method as a Ray task.
          // This will immediately return an object ref (a future) and then create
          // a task that will be executed on a worker process.
          ObjectRef<Integer> res = Ray.task(MyRayApp::myFunction).remote();

          // The result can be retrieved with `ObjectRef::get[.
          Assert.assertTrue(res.get() == 1);

          public class MyRayApp {
            public static int slowFunction() throws InterruptedException {
              TimeUnit.SECONDS.sleep(10);
              return 1;
            }
          }

          // Ray tasks are executed in parallel.
          // All computation is performed in the background, driven by Ray's internal event loop.
          for(int i = 0; i]( 4; i++) {
            // This doesn't block.
            Ray.task(MyRayApp::slowFunction).remote();
          }

    
        
          // A regular C++ function.
          int MyFunction() {
            return 1;
          }
          // Register as a remote function by `RAY_REMOTE`.
          RAY_REMOTE(MyFunction);

          // Invoke the above method as a Ray task.
          // This will immediately return an object ref (a future) and then create
          // a task that will be executed on a worker process.
          auto res = ray::Task(MyFunction).Remote();

          // The result can be retrieved with `ray::ObjectRef::Get`.
          assert(*res.Get() == 1);

          int SlowFunction() {
            std::this_thread::sleep_for(std::chrono::seconds(10));
            return 1;
          }
          RAY_REMOTE(SlowFunction);

          // Ray tasks are executed in parallel.
          // All computation is performed in the background, driven by Ray's internal event loop.
          for(int i = 0; i < 4; i++) {
            // This doesn't block.
            ray::Task(SlowFunction).Remote();
          }

Use `ray summary tasks` from State API  to see running and finished tasks and count:

  # This API is only available when you download Ray via `pip install "ray[default]"`
  ray summary tasks

  ======== Tasks Summary: 2023-05-26 11:09:32.092546 ========
  Stats:
  ------------------------------------
  total_actor_scheduled: 0
  total_actor_tasks: 0
  total_tasks: 5

  Table (group by func_name):
  ------------------------------------
      FUNC_OR_CLASS_NAME    STATE_COUNTS    TYPE
  0   slow_function         RUNNING: 4      NORMAL_TASK
  1   my_function           FINISHED: 1     NORMAL_TASK

Specifying required resources

You can specify resource requirements in tasks (see resource-requirements for more details.)

    
        
    
        
            // Specify required resources.
            Ray.task(MyRayApp::myFunction).setResource("CPU", 4.0).setResource("GPU", 2.0).remote();

    
        
            // Specify required resources.
            ray::Task(MyFunction).SetResource("CPU", 4.0).SetResource("GPU", 2.0).Remote();

Passing object refs to Ray tasks

In addition to values, `Object refs <objects.html) can also be passed into remote functions. When the task gets executed, inside the function body **the argument will be the underlying value**. For example, take this function:

    
        
    
        
            public class MyRayApp {
                public static int functionWithAnArgument(int value) {
                    return value + 1;
                }
            }

            ObjectRef<Integer> objRef1 = Ray.task(MyRayApp::myFunction).remote();
            Assert.assertTrue(objRef1.get() == 1);

            // You can pass an object ref as an argument to another Ray task.
            ObjectRef<Integer> objRef2 = Ray.task(MyRayApp::functionWithAnArgument, objRef1).remote();
            Assert.assertTrue(objRef2.get() == 2);

    
        
            static int FunctionWithAnArgument(int value) {
                return value + 1;
            }
            RAY_REMOTE(FunctionWithAnArgument);

            auto obj_ref1 = ray::Task(MyFunction).Remote();
            assert(*obj_ref1.Get() == 1);

            // You can pass an object ref as an argument to another Ray task.
            auto obj_ref2 = ray::Task(FunctionWithAnArgument).Remote(obj_ref1);
            assert(*obj_ref2.Get() == 2);

Note the following behaviors:

  -  As the second task depends on the output of the first task, Ray will not execute the second task until the first task has finished.
  -  If the two tasks are scheduled on different machines, the output of the
     first task (the value corresponding to `obj_ref1/objRef1`) will be sent over the
     network to the machine where the second task is scheduled.

Waiting for Partial Results

Calling **ray.get** on Ray task results will block until the task finished execution. After launching a number of tasks, you may want to know which ones have
finished executing without blocking on all of them. This could be achieved by ray.wait(). The function
works as follows.

    
        
    
      
        WaitResult<Integer> waitResult = Ray.wait(objectRefs, /*num_returns=*/0, /*timeoutMs=*/1000);
        System.out.println(waitResult.getReady());  // List of ready objects.
        System.out.println(waitResult.getUnready());  // list of unready objects.

    
      
        ray::WaitResult<int> wait_result = ray::Wait(object_refs, /*num_objects=*/0, /*timeout_ms=*/1000);

Generators

Ray is compatible with Python generator syntax. See Ray Generators for more details.

Multiple returns

By default, a Ray task only returns a single Object Ref. However, you can configure Ray tasks to return multiple Object Refs, by setting the `num_returns` option.

    
        
For tasks that return multiple objects, Ray also supports remote generators that allow a task to return one object at a time to reduce memory usage at the worker. Ray also supports an option to set the number of return values dynamically, which can be useful when the task caller does not know how many return values to expect. See the user guide for more details on use cases.

    
        

Cancelling tasks

Ray tasks can be canceled by calling ray.cancel() on the returned Object ref.

    
        

Scheduling

For each task, Ray will choose a node to run it
and the scheduling decision is based on a few factors like
the task's resource requirements,
the specified scheduling strategy
and locations of task arguments.
See Ray scheduling for more details.

Fault Tolerance

By default, Ray will retry failed tasks
due to system failures and specified application-level failures.
You can change this behavior by setting
`max_retries` and `retry_exceptions` options
in ray.remote() and .options().
See Ray fault tolerance for more details.

Task Events

By default, Ray traces the execution of tasks, reporting task status events and profiling events
that the Ray Dashboard and State API use.

You can change this behavior by setting `enable_task_events` options in ray.remote() and .options()
to disable task events, which reduces the overhead of task execution, and the amount of data the task sends to the Ray Dashboard.
Nested tasks don't inherit the task events settings from the parent task. You need to set the task events settings for each task separately.

More about Ray Tasks

    tasks/nested-tasks.rst
