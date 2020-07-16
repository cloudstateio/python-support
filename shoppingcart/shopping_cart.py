"""
Copyright 2020 Lightbend Inc.
Licensed under the Apache License, Version 2.0.
"""

from cloudstate.cloudstate import CloudState
from shoppingcart.shopping_cart_entity import entity as shopping_cart_entity

if __name__ == '__main__':
    CloudState()\
        .port('8080')\
        .register_event_sourced_entity(shopping_cart_entity)\
        .start()
