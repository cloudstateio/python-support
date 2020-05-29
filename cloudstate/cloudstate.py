"""
Copyright 2020 Lightbend Inc.
Licensed under the Apache License, Version 2.0.
"""

from dataclasses import (dataclass, field)
from typing import List
import os

from concurrent import futures
import grpc

from cloudstate.evensourced_servicer import CloudStateEventSourcedServicer
from cloudstate.event_sourced_entity import EventSourcedEntity
from cloudstate.discovery_servicer import CloudStateEntityDiscoveryServicer
from cloudstate.entity_pb2_grpc import add_EntityDiscoveryServicer_to_server
from pprint import pprint

from cloudstate.event_sourced_pb2_grpc import add_EventSourcedServicer_to_server


@dataclass
class CloudState:
    event_sourced_entities: List[EventSourcedEntity] = field(default_factory=list)

    def register_event_sourced_entity(self, entity: EventSourcedEntity):
        self.event_sourced_entities.append(entity)
        return self

    def start(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        add_EntityDiscoveryServicer_to_server(CloudStateEntityDiscoveryServicer(self.event_sourced_entities), server)
        add_EventSourcedServicer_to_server(CloudStateEventSourcedServicer(self.event_sourced_entities), server)
        port = os.environ.get('HOST', '127.0.0.1') + ':' + os.environ.get('PORT', '8080')
        server.add_insecure_port(port)
        pprint('Starting Cloudstate on ' + port)
        server.start()
        server.wait_for_termination()
