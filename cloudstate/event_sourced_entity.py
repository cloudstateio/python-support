from dataclasses import dataclass
from typing import List
from cloudstate.event_sourced_pb2 import _EVENTSOURCED

from google.protobuf import descriptor as _descriptor
@dataclass
class EventSourcedEntity:
    service_descriptor: _descriptor.ServiceDescriptor
    file_descriptors:List[_descriptor.FileDescriptor]
    persistence_id:str=None
    snapshot_every:int =0

    def __post_init__(self):
        if not self.persistence_id:
            self.persistence_id=self.service_descriptor.full_name

    def entity_type(self):
        return _EVENTSOURCED.full_name

    def init_state(self):
        def register_init_state(function):
            """
            Register the function to initialize the state
            """
            #TODO
            return function
        return register_init_state

    def snapshot(self):
        def register_snapshot(function):
            """
            Register the function to snapshot the state
            """
            #TODO
            return function
        return register_snapshot

    def snapshot_handler(self):
        def register_snapshot_handler(function):
            """
            Register the function to handle snapshots
            """
            #TODO
            return function
        return register_snapshot_handler

    def command_handler(self):
        def register_command_handler(function):
            """
            Register the function to handle commands
            """
            #TODO
            return function
        return register_command_handler

    def event_handler(self):
        def register_event_handler(function):
            """
            Register the function to handle events
            """
            #TODO
            return function
        return register_event_handler