# python-support
Python support for [CloudState](https://github.com/cloudstateio/cloudstate)

This repository is an initial setup to get Python Support for CloudState implemented.

By itself CloudState provides great documentation [why](https://cloudstate.io/#why), [what](https://cloudstate.io/#what) and [how](https://cloudstate.io/#contribute) to contribute and [implement](https://cloudstate.io/docs/developer/language-support/index.html#creating-language-support-libraries) a CloudState language support library. This repository particularly tries to help to get Python support for CloudState started if you don't yet know how things work.

# Initial Setup

The following steps can be steps you would take to implement the CloudState user function support library.
Checkboxes that are marked done are steps already done in this repository. The main file to look at is `cloud_state.py`.

- [ ] Get the [CloudState](https://github.com/cloudstateio/cloudstate/) repository cloned as well as [this one](https://github.com/marcellanz/cloudstate_python-support/tree/feature/python-support).
- [ ] Get started to have the TCK of CloudState running and verify their current implementations. You might first read https://cloudstate.io/docs/user/quickstart.html and then https://cloudstate.io/docs/developer/language-support/index.html.
- [ ] Read and try to understand the CloudState protocol defined by the protocols [protobuf files](https://github.com/cloudstateio/cloudstate/tree/master/protocols/protocol/) (The CloudState protocol is specified through these protobuf files),
- [x] Find a gRPC support library of your choice for your language. The gRPC project itself provides [official support](https://packages.grpc.io) with libraries for many languages, but there might be other languages supported by non-official libraries.  
- [x] Copy the *.protobuf files under protocols to your project and compile them with the protoc compiler.
- [x] Start with the implementation of the `EntityDiscovery` service defined in the entity.proto file.
    - this service is the first service the CloudState proxy is calling to get information about the user function library and also which entity types and concrete entities are registered to be used. 
    - the reportError rpc function is helpful during development as the CloudState proxy informs about state and issues it encounters while it communicates with the user function.
- [ ] You may already have your environment prepared tho, but you should install a current version of Python3 and the grpcio-tools module. If you use a dedicated virtual environment you might run:
    - `python3 -m venv cs_env`
    - `./cs_env/bin/pip install grpcio-tools`

The CloudState TCK (the Technology Compatibility Kit) lets you validate the compatibility of your implementation. Before you can run the TCK, you have to add a CloudState TCK configuration section for the Python support in the main CloudState project. This configuration is located at `tck/src/it/resources/application.conf` within the main CloudState repository. 

Add this section to the TCK configuration to the end of it 
```
{
  name = "Akka + Python"
  tck {
    hostname = "0.0.0.0"
    port = 8090
  }
  proxy {
    hostname = "127.0.0.1"
    port = 9000
    directory = ${user.dir}
    command = ["java","-Xmx512M", "-Xms128M", "-Dconfig.resource=in-memory.conf", "-Dcloudstate.proxy.dev-mode-enabled=true", "-jar", "proxy/core/target/scala-2.12/akka-proxy.jar"]
    env-vars {
      USER_FUNCTION_PORT = "8090"
    }
  }
  frontend {
    hostname = "127.0.0.1"
    port = 50051
    directory = ${user.dir}
    command = ["./cs_env/bin/python3", "<path_to>/cloudstate_python-support/cloud_state.py"]
    env-vars {
      HOST = "127.0.0.1"
      PORT = "50051"
    }
  }
}
```
(This command can be used to run the user library manually by yours, perhaps with a debugger attached on so that the TCK does not start it here. 
`command = ["/bin/bash", "-c", "sleep", "900"]`)

An then start the tck by running its integration tests with `sbt tck/it:test`
If it successfully run, you should get something like this on your terminal

```
[info] CloudStateTCK:
[info] The TCK for Akka + Python
[info] - must verify that the user function process responds
[info] - must verify that an initial GetShoppingCart request succeeds *** FAILED ***
[info]   io.grpc.StatusRuntimeException: UNKNOWN: Unexpected entity termination
[info]   at io.grpc.Status.asRuntimeException(Status.java:533)
[info]   at akka.grpc.internal.UnaryCallAdapter.onClose(UnaryCallAdapter.scala:40)
[info]   at io.grpc.PartialForwardingClientCallListener.onClose(PartialForwardingClientCallListener.java:39)
[info]   ...
[info] - must verify that items can be added to, and removed from, a shopping cart *** FAILED ***
[info]   io.grpc.StatusRuntimeException: UNKNOWN: Unexpected entity termination
[info]   at io.grpc.Status.asRuntimeException(Status.java:533)
[info]   at akka.grpc.internal.UnaryCallAdapter.onClose(UnaryCallAdapter.scala:40)
[info]   at io.grpc.PartialForwardingClientCallListener.onClose(PartialForwardingClientCallListener.java:39)
[info]   ...
[info] - must verify that the backend supports the ServerReflection API
[info] - must verify that the HTTP API of ShoppingCart protocol works *** FAILED ***
[info]   400 Bad Request was not equal to 200 OK (CloudStateTCK.scala:503)
[info] Run completed in 47 seconds, 185 milliseconds.
[info] Total number of tests run: 5
[info] Suites: completed 2, aborted 0
[info] Tests: succeeded 2, failed 3, canceled 0, ignored 0, pending 0
[info] *** 3 TESTS FAILED ***
[error] Failed tests:
[error] 	io.cloudstate.tck.TCK
[error] (tck / IntegrationTest / test) sbt.TestsFailedException: Tests unsuccessful
[error] Total time: 54 s, completed Oct 10, 2019 7:34:02 PM
[IJ]sbt:cloudstate> 
```

which says, that two of the 5 TCK tests where successfull and three not so much. A few lines above this, you'd find these lines:

```
2019-10-10 19:33:20.278 INFO akka.cluster.Cluster(akka://cloudstate-proxy) - Cluster Node [akka://cloudstate-proxy@127.0.0.1:25520] - Leader is moving node [akka://cloudstate-proxy@127.0.0.1:25520] to [Up]
protocol_minor_version: 1
proxy_name: "cloudstate-proxy-core"
proxy_version: "0.4.1-105-6097c099-dev"
supported_entity_types: "cloudstate.crdt.Crdt"
supported_entity_types: "cloudstate.eventsourced.EventSourced"

2019-10-10 19:33:21.404 INFO io.cloudstate.proxy.EntityDiscoveryManager - Received EntitySpec from user function with info: ServiceInfo(shopping-cart,0.1.0,Python 3.7.3 [CPython Clang 11.0.0 (clang-1100.0.33.8)],cloudstate-python-support,0.1.0)
2019-10-10 19:33:21.515 DEBUG io.cloudstate.proxy.eventsourced.EventSourcedSupportFactory - Starting EventSourcedEntity for shopping_cart
```

which is the result of the entity spec this minimal of a CloudState user library in `cloud_state.py` returns to the CloudState proxy.

# Next Steps

So from here own you are on your own. There are different paths you could choose from to get the TCK 100%. Depending how your work you could go _Protocol-First_ or _API First_. Regarding the language API, the project aims to have one  that is most idiomatic to the language choosen. So in this case, it should be an API that feels like one a _Pythonista_ would love to work with.

If you are lost a bit, the following steps might help.

- You have to implement the TCK Shopping Cart example, read the implementations of the existing user functions support libraries.
- After you implemented the Entitiy Discovery service, go ahead and implement the `EventSourced` service defined in `event_sourced.proto`.
    - having this, you should be ready to pass all TCK tests. 
    - you most probably have to read certain details out of existing language Shopping Cart implementations as not everything is defined in the protobuf files spec-wise.
- Implement the protobuf _Any-encoding_ defined by the [CloudState serialization convention](https://cloudstate.io/docs/developer/language-support/serialization.html).
- Document the language support and the API under `docs/src/main/paradox/user/lang/python`
- Provide support so that the TCK can build build the language support and run the TCK Shopping Cart example within the main repository.
- Implement the CRDT Support.