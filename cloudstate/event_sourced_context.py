from cloudstate.contexts import ClientActionContext


class EventSourcedCommandContext(ClientActionContext):
    """An event sourced command context.
    Command Handler Methods may take this is a parameter. It allows emitting
    new events in response to a command, along with forwarding the result to other entities, and
    performing side effects on other entities"""

    def emit(self, event):
        """Emit the given event. The event will be persisted, and the handler of the event defined in the
        current behavior will immediately be executed to pick it up"""
        pass
