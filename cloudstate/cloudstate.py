"""
Copyright 2020 Lightbend Inc.
Licensed under the Apache License, Version 2.0.
"""
from typing import Optional

from dataclasses import (dataclass, field)
from typing import List
import os

from concurrent import futures
import grpc

from cloudstate.evensourced_servicer import CloudStateEventSourcedServicer
from cloudstate.event_sourced_entity import EventSourcedEntity
from cloudstate.discovery_servicer import CloudStateEntityDiscoveryServicer
from cloudstate.entity_pb2_grpc import add_EntityDiscoveryServicer_to_server

import logging

from cloudstate.event_sourced_pb2_grpc import add_EventSourcedServicer_to_server

@dataclass
class CloudState:
    logging.basicConfig(format='%(asctime)s - %(filename)s - %(levelname)s: %(message)s', level=logging.INFO)
    logging.root.setLevel(logging.NOTSET)

    __host = '127.0.0.1'
    __port = '8080'
    __workers = 10
    __event_sourced_entities: List[EventSourcedEntity] = field(default_factory=list)

    def host(self, address: str):
        """Set the Network Host address."""
        self.__host = address
        return self

    def port(self, port: str):
        """Set the Network Port address."""
        self.__port = port
        return self

    def max_workers(self, workers: Optional[int] = 10):
        """Set the gRPC Server number of Workers."""
        self.__workers = workers
        return self

    def register_event_sourced_entity(self, entity: EventSourcedEntity):
        """Registry the user EventSourced entity."""
        self.__event_sourced_entities.append(entity)
        return self

    def start(self):
        """Start the user function and gRPC Server."""
        address = '{}:{}'.format(os.environ.get('HOST', self.__host), os.environ.get('PORT', self.__port))
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.__workers))
        add_EntityDiscoveryServicer_to_server(CloudStateEntityDiscoveryServicer(self.__event_sourced_entities), server)
        add_EventSourcedServicer_to_server(CloudStateEventSourcedServicer(self.__event_sourced_entities), server)

        logging.info('Starting Cloudstate on address %s', address)
        try:
            server.add_insecure_port(address)
            server.start()
        except IOError as e:
            logging.error('Error on start Cloudstate %s', e.__cause__)

        server.wait_for_termination()
