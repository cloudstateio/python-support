"""
Copyright 2020 Lightbend Inc.
Licensed under the Apache License, Version 2.0.
"""

import inspect
import logging
from dataclasses import dataclass, field
from typing import Callable, List, MutableMapping

from google.protobuf import descriptor as _descriptor

from cloudstate.action_context import ActionContext
from cloudstate.action_pb2 import _ACTIONPROTOCOL


@dataclass
class Action:
    service_descriptor: _descriptor.ServiceDescriptor
    file_descriptors: List[_descriptor.FileDescriptor]
    unary_handlers: MutableMapping[str, Callable] = field(default_factory=dict)
    stream_handlers: MutableMapping[str, Callable] = field(default_factory=dict)
    stream_in_handlers: MutableMapping[str, Callable] = field(default_factory=dict)
    stream_out_handlers: MutableMapping[str, Callable] = field(default_factory=dict)

    @property
    def persistence_id(self):
        return self.name()

    def entity_type(self):
        return _ACTIONPROTOCOL.full_name

    def unary_handler(self, name: str):
        def register_unary_handler(function):
            """
            Register the function to handle commands
            """
            if name in self.unary_handlers:
                raise Exception(
                    "Command handler function {} already defined for command {}".format(
                        self.unary_handlers[name], name
                    )
                )
            if function.__code__.co_argcount > 2:
                raise Exception(
                    "At most two parameters, the command and the context, should be "
                    "accepted by the command_handler function"
                )
            self.unary_handlers[name] = function
            return function

        return register_unary_handler

    def stream_handler(self, name: str):
        def register_stream_handler(function):
            """
            Register the function to handle commands
            """
            if name in self.stream_handlers:
                raise Exception(
                    "Command handler function {} already defined for command {}".format(
                        self.unary_handlers[name], name
                    )
                )
            if function.__code__.co_argcount > 2:
                raise Exception(
                    "At most two parameters, the command and the context, should be "
                    "accepted by the command_handler function"
                )
            self.stream_handlers[name] = function
            return function

        return register_stream_handler

    def stream_in_handler(self, name: str):
        def register_stream_in_handler(function):
            """
            Register the function to handle commands
            """
            if name in self.stream_in_handlers:
                raise Exception(
                    "Command handler function {} already defined for command {}".format(
                        self.unary_handlers[name], name
                    )
                )
            if function.__code__.co_argcount > 2:
                raise Exception(
                    "At most two parameters, the command and the context, should be "
                    "accepted by the command_handler function"
                )
            self.stream_in_handlers[name] = function
            return function

        return register_stream_in_handler

    def stream_out_handler(self, name: str):
        def register_stream_out_handler(function):
            """
            Register the function to handle commands
            """
            if name in self.stream_out_handlers:
                raise Exception(
                    "Command handler function {} already defined for command {}".format(
                        self.unary_handlers[name], name
                    )
                )
            if function.__code__.co_argcount > 2:
                raise Exception(
                    "At most two parameters, the command and the context, should be "
                    "accepted by the command_handler function"
                )
            self.stream_out_handlers[name] = function
            return function

        return register_stream_out_handler

    def name(self):
        return self.service_descriptor.full_name


def invoke(function, parameters):
    ordered_parameters = []
    for parameter_definition in inspect.signature(function).parameters.values():
        annotation = parameter_definition.annotation
        if annotation == inspect._empty:
            raise Exception(
                f"Cannot inject parameter {parameter_definition.name} of function "
                f"{function}: Missing type annotation"
            )
        match_found = False
        for param in parameters:
            if isinstance(param, annotation):
                match_found = True
                ordered_parameters.append(param)
        if not match_found:
            raise Exception(
                "Cannot inject parameter {} of function {}: No matching value".format(
                    parameter_definition.name, function
                )
            )
    return function(*ordered_parameters)


class ActionHandler:
    def __init__(self, function: Action):
        self.function: Action = function
        self.logger = logging.getLogger(f"ActionHandler {function.name()}")

    def handle_unary(self, command, ctx: ActionContext):
        if ctx.command_name not in self.function.unary_handlers:
            raise Exception(
                "Missing command handler function for entity {} and command {}".format(
                    self.function.name(), ctx.command_name
                )
            )
        return invoke(self.function.unary_handlers[ctx.command_name], [command, ctx])

    def handle_stream(self, command, ctx: ActionContext):
        self.logger.info(f"handling stream: {command} {ctx}")
        if ctx.command_name not in self.function.stream_handlers:
            raise Exception(
                "Missing command handler function for entity {} and command {}".format(
                    self.function.name(), ctx.command_name
                )
            )
        return invoke(self.function.stream_handlers[ctx.command_name], [command, ctx])

    def handle_stream_in(self, command, ctx: ActionContext):
        if ctx.command_name not in self.function.stream_in_handlers:
            raise Exception(
                "Missing command handler function for entity {} and command {}".format(
                    self.function.name(), ctx.command_name
                )
            )
        return invoke(
            self.function.stream_in_handlers[ctx.command_name], [command, ctx]
        )

    def handle_stream_out(self, command, ctx: ActionContext):
        if ctx.command_name not in self.function.stream_out_handlers:
            raise Exception(
                "Missing command handler function for entity {} and command {}".format(
                    self.function.name(), ctx.command_name
                )
            )
        return invoke(
            self.function.stream_out_handlers[ctx.command_name], [command, ctx]
        )
