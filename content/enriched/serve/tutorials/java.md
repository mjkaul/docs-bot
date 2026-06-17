---
id: serve.tutorials.java
title: Java
topic_type: task
description: ''
subjects:
- serve
- core
mentions:
- deployment
- replica
- task
references: []
canonical_path: /en/latest/serve/tutorials/java
source: https://github.com/ray-project/ray/blob/master/doc/source/serve/tutorials/java.md
license: Apache 2.0, The Ray Authors
---

---
orphan: true
---

# Serve a Java App

To use Java Ray Serve, you need the following dependency in your pom.xml.

```xml
<dependency>
  <groupId>io.ray</groupId>
  <artifactId>ray-serve</artifactId>
  <version>${ray.version}</version>
  <scope>provided</scope>
</dependency>
```

> NOTE: After installing Ray with Python, the local environment includes the Java jar of Ray Serve. The `provided` scope ensures that you can compile the Java code using Ray Serve without version conflicts when you deploy on the cluster.

## Example model

This example use case is a production workflow for a financial application. The application needs to compute the best strategy to interact with different banks for a single task.

[code example]

This example uses the `Strategy` class to calculate the indicators of a number of banks.

* The `calc` method is the entry of the calculation. The input parameters are the time interval of calculation and the map of the banks and their indicators. The `calc` method contains a two-tier `for` loop, traversing each indicator list of each bank, and calling the `calcBankIndicators` method to calculate the indicators of the specified bank.

- There is another layer of `for` loop in the `calcBankIndicators` method, which traverses each indicator, and then calls the `calcIndicator` method to calculate the specific indicator of the bank.
- The `calcIndicator` method is a specific calculation logic based on the bank, the specified time interval and the indicator.

This code uses the `Strategy` class:

[code example]

When the scale of banks and indicators expands, the three-tier `for` loop slows down the calculation. Even if you use the thread pool to calculate each indicator in parallel, you may encounter a single machine performance bottleneck. Moreover, you can't use this `Strategy` object as a resident service.

## Converting to a Ray Serve Deployment

Through Ray Serve, you can deploy the core computing logic of `Strategy` as a scalable distributed computing service.

First, extract the indicator calculation of each institution into a separate `StrategyOnRayServe` class:

[code example]

Next, start the Ray Serve runtime and deploy `StrategyOnRayServe` as a deployment.

[code example]

The `Deployment.create` makes a Deployment object named `strategy`. After executing `Deployment.deploy`, the Ray Serve instance deploys this `strategy` deployment with four replicas, and you can access it for distributed parallel computing.

## Testing the Ray Serve Deployment

You can test the `strategy` deployment using RayServeHandle inside Ray:

[code example]

This code executes the calculation of each bank's indicator serially, and sends it to Ray for execution. You can make the calculation concurrent, which not only improves the calculation efficiency, but also solves the bottleneck of single machine.

[code example]

You can use `StrategyCalcOnRayServe` like the example in the `main` method:

[code example]

## Calling Ray Serve Deployment with HTTP

Another way to test or call a deployment is through the HTTP request. However, two limitations exist for the Java deployments:

- Only the `call` method of the user class can process the HTTP requests.

- The `call` method can only have one input parameter, and the type of the input parameter and the returned value can only be `String`.

If you want to call the `strategy` deployment with HTTP, then you can rewrite the class like this code:

[code example]

After deploying this deployment, you can access it with the `curl` command:

```shell
curl -d '{"time":1641038674, "bank":"test_bank", "indicator":"test_indicator"}' http://127.0.0.1:8000/strategy
```

You can also access it using HTTP Client in Java code:

[code example]

The example of strategy calculation using HTTP to access deployment is as follows:

[code example]

You can also rewrite this code to support concurrency:

[code example]

Finally, the complete usage of `HttpStrategyCalcOnRayServe` is like this code:

[code example]
