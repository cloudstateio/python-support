"""
Copyright 2020 Lightbend Inc.
Licensed under the Apache License, Version 2.0.
"""

from typing import Iterator

from cloudstate.action_context import ActionContext
from cloudstate.action_protocol_entity import Action
from cloudstate.test.actiondemo.actiondemo2_pb2 import _ACTIONDEMO2
from cloudstate.test.actiondemo.actiondemo2_pb2 import DESCRIPTOR as FILE_DESCRIPTOR2
from cloudstate.test.actiondemo.actiondemo2_pb2 import (
    FunctionRequest2,
    FunctionResponse2,
)
from cloudstate.test.actiondemo.actiondemo_pb2 import _ACTIONDEMO
from cloudstate.test.actiondemo.actiondemo_pb2 import DESCRIPTOR as FILE_DESCRIPTOR
from cloudstate.test.actiondemo.actiondemo_pb2 import (
    FunctionRequest,
    FunctionResponse,
    SumTotal,
)

definition = Action(_ACTIONDEMO, [FILE_DESCRIPTOR])


@definition.unary_handler("ReverseString")
def reverse_string(arg: FunctionRequest, ctx: ActionContext) -> FunctionResponse:
    if arg.foo == "boom":
        ctx.fail("Intentionally failed.")
    else:
        return FunctionResponse(bar=arg.foo[::-1])


@definition.stream_handler("ReverseStrings")
def reverse_strings(arg: Iterator, ctx: ActionContext) -> Iterator[FunctionResponse]:
    for element in arg:
        if element.foo == "boom":
            ctx.fail("Intentionally failed.")

        yield FunctionResponse(bar=element.foo[::-1])


@definition.stream_in_handler("SumStream")
def sum_stream(
    arg: Iterator,  # todo, really need generics on this api but the
    # reflection api doesn't allow it..
    ctx: ActionContext,
) -> SumTotal:
    total = 0
    for element in arg:
        if element.quantity < 0:
            ctx.fail("Intentionally failed.")
        total += element.quantity

    return SumTotal(total=total)


@definition.stream_out_handler("SillyLetterStream")
def silly_letter_stream(arg: FunctionRequest, ctx: ActionContext) -> SumTotal:
    if arg.foo == "nope":
        ctx.fail("Intentionally failed.")
    letters = list(arg.foo)
    for letter in letters:
        yield FunctionResponse(bar=letter + "!!")


definition2 = Action(_ACTIONDEMO2, [FILE_DESCRIPTOR2])


@definition2.unary_handler("ReverseString2")
def reverse_string2(arg: FunctionRequest2, ctx: ActionContext) -> FunctionResponse2:
    if arg.foo == "boom":
        ctx.fail("Intentionally failed.")

    else:
        return FunctionResponse2(bar=arg.foo[::-1] + "!")
