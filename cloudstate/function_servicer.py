"""
Copyright 2020 Lightbend Inc.
Licensed under the Apache License, Version 2.0.
"""

import logging
from typing import List

import grpc
from google.protobuf import symbol_database as _symbol_database
from grpc._server import _RequestIterator

from cloudstate.entity_pb2 import ClientAction
from cloudstate.function_pb2 import FunctionCommand, FunctionReply
from cloudstate.function_pb2_grpc import StatelessFunctionServicer
from cloudstate.stateless_function_context import StatelessFunctionContext
from cloudstate.stateless_function_entity import (
    StatelessFunction,
    StatelessFunctionHandler,
)
from cloudstate.utils.payload_utils import get_payload

_sym_db = _symbol_database.Default()

TYPE_URL_PREFIX = "type.googleapis.com/"


class CloudStateStatelessFunctionServicer(StatelessFunctionServicer):
    def __init__(self, stateless_function_entities: List[StatelessFunction]):
        self.stateless_function_entities = {
            entity.name(): entity for entity in stateless_function_entities
        }
        assert len(stateless_function_entities) == len(self.stateless_function_entities)

    def handleUnary(self, request: FunctionCommand, context):
        logging.info(f"handling unary {request} {context}.")
        if request.service_name in self.stateless_function_entities:
            service = self.stateless_function_entities[request.service_name]
            handler = StatelessFunctionHandler(service)
            ctx = StatelessFunctionContext(request.name)
            result = None
            try:
                result = handler.handle_unary(
                    get_payload(request), ctx
                )  # the proto the user defined function returned.
            except Exception as ex:
                ctx.fail(str(ex))
                logging.exception("Failed to execute command:" + str(ex))

            client_action: ClientAction = ctx.create_client_action(result, False)
            function_reply = FunctionReply()

            if not ctx.has_errors():
                function_reply.side_effects.extend(ctx.effects)
                if client_action.HasField("reply"):
                    function_reply.reply.CopyFrom(client_action.reply)
                elif client_action.HasField("forward"):
                    function_reply.forward.CopyFrom(client_action.forward)
            else:
                function_reply.failure.CopyFrom(client_action.failure)
            return function_reply

    def handleStreamed(self, request_iterator: _RequestIterator, context):
        peek = request_iterator.next()  # evidently, the first message has no payload
        # and is probably intended to prime the stream handler.
        if peek.service_name in self.stateless_function_entities:
            handler = StatelessFunctionHandler(
                self.stateless_function_entities[peek.service_name]
            )
            logging.debug(f"set stream handler to {peek.service_name}")
        else:
            context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            context.set_details("Method not implemented!")
            raise NotImplementedError("Method not implemented!")

        reconstructed = (get_payload(x) for x in request_iterator)
        ctx = StatelessFunctionContext(peek.name)
        try:
            result = handler.handle_stream(
                reconstructed, ctx
            )  # the proto the user defined function returned.
            for r in result:
                client_action = ctx.create_client_action(r, False)
                function_reply = FunctionReply()
                if not ctx.has_errors():
                    function_reply.side_effects.extend(ctx.effects)
                    if client_action.HasField("reply"):
                        function_reply.reply.CopyFrom(client_action.reply)
                    elif client_action.HasField("forward"):
                        function_reply.forward.CopyFrom(client_action.forward)
                else:
                    function_reply.failure.CopyFrom(client_action.failure)
                yield function_reply

        except Exception as ex:
            ctx.fail(str(ex))
            logging.exception("Failed to execute command:" + str(ex))

    def handleStreamedIn(self, request_iterator, context):
        peek = request_iterator.next()  # evidently, the first message has no payload
        # and is probably intended to prime the stream handler.
        logging.debug(f"peeked: {peek}")
        if peek.service_name in self.stateless_function_entities:
            handler = StatelessFunctionHandler(
                self.stateless_function_entities[peek.service_name]
            )
            logging.debug(f"set stream in handler to {peek.service_name}")
        else:
            context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            context.set_details("Method not implemented!")
            raise NotImplementedError("Method not implemented!")

        reconstructed = (get_payload(x) for x in request_iterator)
        ctx = StatelessFunctionContext(peek.name)
        try:
            result = handler.handle_stream_in(
                reconstructed, ctx
            )  # the proto the user defined function returned.
            client_action = ctx.create_client_action(result, False)
            function_reply = FunctionReply()
            if not ctx.has_errors():
                function_reply.side_effects.extend(ctx.effects)
                if client_action.HasField("reply"):
                    function_reply.reply.CopyFrom(client_action.reply)
                elif client_action.HasField("forward"):
                    function_reply.forward.CopyFrom(client_action.forward)
            else:
                function_reply.failure.CopyFrom(client_action.failure)
            return function_reply

        except Exception as ex:
            ctx.fail(str(ex))
            logging.exception("Failed to execute command:" + str(ex))

    def handleStreamedOut(self, request, context):
        if request.service_name in self.stateless_function_entities:
            handler = StatelessFunctionHandler(
                self.stateless_function_entities[request.service_name]
            )
        else:
            context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            context.set_details("Method not implemented!")
            raise NotImplementedError("Method not implemented!")

        reconstructed = get_payload(request)
        ctx = StatelessFunctionContext(request.name)
        try:
            for result in handler.handle_stream_out(reconstructed, ctx):
                client_action = ctx.create_client_action(result, False)
                function_reply = FunctionReply()
                if not ctx.has_errors():
                    function_reply.side_effects.extend(ctx.effects)
                    if client_action.HasField("reply"):
                        function_reply.reply.CopyFrom(client_action.reply)
                    elif client_action.HasField("forward"):
                        function_reply.forward.CopyFrom(client_action.forward)
                else:
                    function_reply.failure.CopyFrom(client_action.failure)
                yield function_reply

        except Exception as ex:
            ctx.fail(str(ex))
            logging.exception("Failed to execute command:" + str(ex))
