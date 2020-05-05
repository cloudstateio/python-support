from dataclasses import dataclass, field
from typing import List, Any

from cloudstate.contexts import ClientActionContext

@dataclass
class EventSourcedCommandContext(ClientActionContext):
    """An event sourced command context.
    Command Handler Methods may take this is a parameter. It allows emitting
    new events in response to a command, along with forwarding the result to other entities, and
    performing side effects on other entities"""
    command_name:str
    command_id:int
    entity_id:str
    sequence:int
    events:List[Any]=field(default_factory=list)


    def emit(self, event):
        """Emit the given event. The event will be persisted, and the handler of the event defined in the
        current behavior will immediately be executed to pick it up"""
        self.events.append(event)

@dataclass
class SnapshotContext:
    entity_id:str
    sequence_number: int


@dataclass
class EventContext:
    entity_id: str
    sequence_number:int