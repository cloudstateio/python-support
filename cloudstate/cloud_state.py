from dataclasses import (dataclass, field)
from typing import List
import os

from concurrent import futures
import grpc

from cloudstate.event_sourced_entity import EventSourcedEntity
from cloudstate.discovery_servicer import CloudStateEntityDiscoveryServicer
from cloudstate.entity_pb2_grpc import add_EntityDiscoveryServicer_to_server
from pprint import pprint


@dataclass
class CloudState:
    event_sourced_entities: List[EventSourcedEntity] = field(default_factory=list)

    def register_event_sourced_entity(self, entity: EventSourcedEntity):
        self.event_sourced_entities.append(entity)
        return self

    def serve(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        add_EntityDiscoveryServicer_to_server(CloudStateEntityDiscoveryServicer(self.event_sourced_entities), server)
        port = os.environ.get('HOST', '127.0.0.1') + ':' + os.environ.get('PORT', '50051')
        server.add_insecure_port(port)
        pprint('Starting CloudStateEntityDiscoveryServicer on ' + port)
        server.start()
        server.wait_for_termination()
