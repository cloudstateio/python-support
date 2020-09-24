"""
Copyright 2020 Lightbend Inc.
Licensed under the Apache License, Version 2.0.
"""

import logging

from cloudstate.cloudstate import CloudState
from cloudstate.test.functiondemo.function_definition import definition, definition2
from cloudstate.test.shoppingcart import shopping_cart_entity

logger = logging.getLogger()


def run_test_server(
    run_shopping_cart: bool = True, run_function_demo: bool = True, port: int = 8080
):
    server_builder = CloudState().host("0.0.0.0").port(str(port))
    if run_shopping_cart:
        logger.info("adding shoppingcart service")
        server_builder = server_builder.register_event_sourced_entity(
            shopping_cart_entity.entity
        )
    if run_function_demo:
        logger.info("adding functiondemo service")
        server_builder = server_builder.register_stateless_function_entity(definition)
        server_builder = server_builder.register_stateless_function_entity(definition2)

    return server_builder.start()
