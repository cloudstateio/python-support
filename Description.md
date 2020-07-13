
Cloudstate is a specification, protocol, and reference implementation for providing distributed state management patterns suitable for **Serverless** computing. 
The current supported and envisioned patterns include:

* **Event Sourcing**
* **Conflict-Free Replicated Data Types (CRDTs)**
* **Key-Value storage**
* **P2P messaging**
* **CQRS read side projections**

Cloudstate is polyglot, which means that services can be written in any language that supports gRPC, 
and with language specific libraries provided that allow idiomatic use of the patterns in each language. 
Cloudstate can be used either by itself, in combination with a Service Mesh, 
or it is envisioned that it will be integrated with other Serverless technologies such as [Knative](https://knative.dev/).

Read more about the design, architecture, techniques, and technologies behind Cloudstate in [this section in the documentation](https://github.com/cloudstateio/cloudstate/blob/master/README.md#enter-cloudstate). 

The Cloudstate Python user language support is a library that implements the Cloudstate protocol and offers an pythonistic API 
for writing entities that implement the types supported by the Cloudstate protocol.

The Cloudstate documentation can be found [here](https://cloudstate.io/docs/)

## Install and update using pip:

```
pip install -U cloudstate
```

## A Simple EventSourced Example:

### 1. Define your gRPC contract

```
// This is the public API offered by the shopping cart entity.
syntax = "proto3";

import "google/protobuf/empty.proto";
import "cloudstate/entity_key.proto";
import "google/api/annotations.proto";
import "google/api/http.proto";

package com.example.shoppingcart;

message AddLineItem {
    string user_id = 1 [(.cloudstate.entity_key) = true];
    string product_id = 2;
    string name = 3;
    int32 quantity = 4;
}

message RemoveLineItem {
    string user_id = 1 [(.cloudstate.entity_key) = true];
    string product_id = 2;
}

message GetShoppingCart {
    string user_id = 1 [(.cloudstate.entity_key) = true];
}

message LineItem {
    string product_id = 1;
    string name = 2;
    int32 quantity = 3;
}

message Cart {
    repeated LineItem items = 1;
}

service ShoppingCart {
    rpc AddItem(AddLineItem) returns (google.protobuf.Empty) {
        option (google.api.http) = {
            post: "/cart/{user_id}/items/add",
            body: "*",
        };
    }

    rpc RemoveItem(RemoveLineItem) returns (google.protobuf.Empty) {
        option (google.api.http).post = "/cart/{user_id}/items/{product_id}/remove";
    }

    rpc GetCart(GetShoppingCart) returns (Cart) {
        option (google.api.http) = {
          get: "/carts/{user_id}",
          additional_bindings: {
            get: "/carts/{user_id}/items",
            response_body: "items"
          }
        };
    }
}

```

### 2. Generate Python files

It is necessary to compile your .proto files using the protoc compiler in order to generate Python files. 
See [this official gRPC for Python quickstart](https://grpc.io/docs/languages/python/quickstart/) if you are not familiar with the gRPC protocol.

Here is an example of how to compile the sample proto file:
```
python -m grpc_tools.protoc -I../../protos --python_out=. --grpc_python_out=. ../../protos/shoppingcart.proto
```

### 3. Implement your business logic under an EventSourced Cloudstate Entity

```
from dataclasses import dataclass, field
from typing import MutableMapping

from google.protobuf.empty_pb2 import Empty

from cloudstate.event_sourced_context import EventSourcedCommandContext
from cloudstate.event_sourced_entity import EventSourcedEntity
from shoppingcart.domain_pb2 import (Cart as DomainCart, LineItem as DomainLineItem, ItemAdded, ItemRemoved)
from shoppingcart.shoppingcart_pb2 import (Cart, LineItem, AddLineItem, RemoveLineItem)
from shoppingcart.shoppingcart_pb2 import (_SHOPPINGCART, DESCRIPTOR as FILE_DESCRIPTOR)


@dataclass
class ShoppingCartState:
    entity_id: str
    cart: MutableMapping[str, LineItem] = field(default_factory=dict)


def init(entity_id: str) -> ShoppingCartState:
    return ShoppingCartState(entity_id)


entity = EventSourcedEntity(_SHOPPINGCART, [FILE_DESCRIPTOR], init)


def to_domain_line_item(item):
    domain_item = DomainLineItem()
    domain_item.productId = item.product_id
    domain_item.name = item.name
    domain_item.quantity = item.quantity
    return domain_item


@entity.snapshot()
def snapshot(state: ShoppingCartState):
    cart = DomainCart()
    cart.items = [to_domain_line_item(item) for item in state.cart.values()]
    return cart


def to_line_item(domain_item):
    item = LineItem()
    item.product_id = domain_item.productId
    item.name = domain_item.name
    item.quantity = domain_item.quantity
    return item


@entity.snapshot_handler()
def handle_snapshot(state: ShoppingCartState, domain_cart: DomainCart):
    state.cart = {domain_item.productId: to_line_item(domain_item) for domain_item in domain_cart.items}


@entity.event_handler(ItemAdded)
def item_added(state: ShoppingCartState, event: ItemAdded):
    cart = state.cart
    if event.item.productId in cart:
        item = cart[event.item.productId]
        item.quantity = item.quantity + event.item.quantity
    else:
        item = to_line_item(event.item)
        cart[item.product_id] = item


@entity.event_handler(ItemRemoved)
def item_removed(state: ShoppingCartState, event: ItemRemoved):
    del state.cart[event.productId]


@entity.command_handler("GetCart")
def get_cart(state: ShoppingCartState):
    cart = Cart()
    cart.items.extend(state.cart.values())
    return cart


@entity.command_handler("AddItem")
def add_item(item: AddLineItem, ctx: EventSourcedCommandContext):
    if item.quantity <= 0:
        ctx.fail("Cannot add negative quantity of to item {}".format(item.productId))
    else:
        item_added_event = ItemAdded()
        item_added_event.item.CopyFrom(to_domain_line_item(item))
        ctx.emit(item_added_event)
    return Empty()


@entity.command_handler("RemoveItem")
def remove_item(state: ShoppingCartState, item: RemoveLineItem, ctx: EventSourcedCommandContext):
    cart = state.cart
    if item.product_id not in cart:
        ctx.fail("Cannot remove item {} because it is not in the cart.".format(item.productId))
    else:
        item_removed_event = ItemRemoved()
        item_removed_event.productId = item.product_id
        ctx.emit(item_removed_event)
    return Empty()
```

### 4. Register Entity

```
from cloudstate.cloudstate import CloudState
from shoppingcart.shopping_cart_entity import entity as shopping_cart_entity
import logging

if __name__ == '__main__':
    logging.basicConfig()
    CloudState().register_event_sourced_entity(shopping_cart_entity).start()
```

### 5. Deployment

Cloudstate runs on Docker and Kubernetes you need to package your application so that it works as a Docker container 
and can deploy it together with Cloudstate Operator on Kubernetes, the details and examples of all of which can be found [here](https://code.visualstudio.com/docs/containers/quickstart-python), [here](https://github.com/cloudstateio/python-support/blob/master/shoppingcart/Dockerfile) and [here](https://cloudstate.io/docs/core/current/user/deployment/index.html).

## Contributing

For guidance on setting up a development environment and how to make a contribution to Cloudstate, 
see the contributing [project page](https://github.com/cloudstateio/python-support) or consult an official documentation [here](https://cloudstate.io/docs/).

## Links

* [Website](https://cloudstate.io/)
* [Documentation](https://cloudstate.io/docs/)
* [Releases](https://pypi.org/project/cloudstate/)
* [Code](https://github.com/cloudstateio/python-support)
* [Issue tracker](https://github.com/cloudstateio/python-support/issues)
