# Getting started
## Prerequisites

Python version
: Cloudstate Python support requires at least Python 3.7
##Install current version:

@@@vars
```
pip install cloudstate==$cloudstate.python.version$
```
@@@

## Protobuf files

We recommend using [grpc tools](https://grpc.io/docs/languages/python/quickstart/) to generate python code from your descriptor files and use the generated code as a starting point to implement your cloudstate entities

please check the [event sourcing](eventsourced.md) shopping cart example for details
## Creating a main function

Your main class will be responsible for creating the Cloudstate gRPC server, registering the entities for it to serve, and starting it. To do this, you can use the `cloudstate` function server builder, for example:

@@snip [Main.kt](/docs/src/test/kotlin/docs/user/gettingstarted/Main.kt) { #shopping-cart-main }

We will see more details on registering entities in the coming pages.

## Parameter injection

Cloudstate entities work by annotating classes and functions to be instantiated and invoked by the Cloudstate server. The functions and constructors invoked by the server can be injected with parameters of various types from the context of the invocation. For example, an `@CommandHandler` annotated function may take an argument for the message type for that gRPC service call, in addition it may take a `CommandContext` parameter.

Exactly which context parameters are available depend on the type of entity and the type of handler, in subsequent pages we'll detail which parameters are available in which circumstances. The order of the parameters in the function signature can be anything, parameters are matched by type and sometimes by annotation. The following context parameters are available in every context:

| Type                                | Annotation   | Description           |
|-------------------------------------|--------------|-----------------------|
| `io.cloudstate.javasupport.Context` |              | The super type of all Cloudstate contexts. Every invoker makes a subtype of this available for injection, and method or constructor may accept that sub type, or any super type of that subtype that is a subtype of `Context`. |
| `java.lang.String`                  | `@EntityId`  | The ID of the entity. |  