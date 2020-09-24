"""
Copyright 2020 Lightbend Inc.
Licensed under the Apache License, Version 2.0.
"""

from dataclasses import dataclass, field
from typing import MutableMapping

from google.protobuf.empty_pb2 import Empty

from cloudstate.event_sourced_context import EventSourcedCommandContext
from cloudstate.event_sourced_entity import EventSourcedEntity
from cloudstate.test.shoppingcart.persistence.domain_pb2 import Cart as DomainCart
from cloudstate.test.shoppingcart.persistence.domain_pb2 import ItemAdded, ItemRemoved
from cloudstate.test.shoppingcart.persistence.domain_pb2 import (
    LineItem as DomainLineItem,
)
from cloudstate.test.shoppingcart.shoppingcart_pb2 import _SHOPPINGCART
from cloudstate.test.shoppingcart.shoppingcart_pb2 import DESCRIPTOR as FILE_DESCRIPTOR
from cloudstate.test.shoppingcart.shoppingcart_pb2 import (
    AddLineItem,
    Cart,
    GetShoppingCart,
    LineItem,
    RemoveLineItem,
)


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
    state.cart = {
        domain_item.productId: to_line_item(domain_item)
        for domain_item in domain_cart.items
    }


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
def get_cart(
    state: ShoppingCartState, item: GetShoppingCart, ctx: EventSourcedCommandContext
):
    cart = Cart()
    cart.items.extend(state.cart.values())

    return cart


@entity.command_handler("AddItem")
def add_item(item: AddLineItem, ctx: EventSourcedCommandContext):
    if item.quantity <= 0:
        ctx.fail(
            f"Cannot add negative quantity of to item {item.product_id} at request "
            f"{item}"
        )
    else:
        item_added_event = ItemAdded()
        item_added_event.item.CopyFrom(to_domain_line_item(item))
        ctx.emit(item_added_event)
    return Empty()


@entity.command_handler("RemoveItem")
def remove_item(
    state: ShoppingCartState, item: RemoveLineItem, ctx: EventSourcedCommandContext
):
    cart = state.cart
    if item.product_id not in cart:
        ctx.fail(
            "Cannot remove item {} because it is not in the cart.".format(
                item.product_id
            )
        )
    else:
        item_removed_event = ItemRemoved()
        item_removed_event.productId = item.product_id
        ctx.emit(item_removed_event)
    return Empty()
