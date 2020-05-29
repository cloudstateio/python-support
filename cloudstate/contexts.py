"""
Copyright 2020 Lightbend Inc.
Licensed under the Apache License, Version 2.0.
"""

from dataclasses import dataclass, field
from typing import List

from cloudstate.entity_pb2 import ClientAction, Failure, Reply, Forward, SideEffect


class Context:
    """Root class of all contexts."""
    pass


class ClientActionContext(Context):
    """Context that provides client actions, which include failing and forwarding.
    These contexts are typically made available in response to commands."""

    def __init__(self,command_id: int):
        self.command_id: int = command_id
        self.errors: List[str] = []
        self.effects:List[SideEffect] = []
        self.forward: Forward = None

    def fail(self, error_message: str):
        """Fail the command with the given message"""
        self.errors.append(error_message)

    def has_errors(self):
        return len(self.errors) > 0

    def create_client_action(self, result, allow_reply):
        client_action = ClientAction()
        if self.has_errors():
            failure = Failure()
            failure.command_id = self.command_id
            failure.description = str(self.errors)
            client_action.failure.CopyFrom(failure)
        elif result:
            if self.forward:
                raise Exception("Both a reply was returned, and a forward message was sent, choose one or the other.")
            else:
                reply = Reply()
                reply.payload.Pack(result)
                client_action.reply.CopyFrom(reply)
        elif self.forward:
            client_action.forward.CopyFrom(self.forward)
        elif allow_reply:
            return None
        else:
            raise Exception("No reply or forward returned by command handler!")
        return client_action
