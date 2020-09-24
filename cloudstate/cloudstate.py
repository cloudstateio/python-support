"""
Copyright 2020 Lightbend Inc.
Licensed under the Apache License, Version 2.0.
"""
import logging
import multiprocessing
import os
from concurrent import futures
from dataclasses import dataclass, field
from typing import List, Optional

import grpc

from cloudstate.discovery_servicer import CloudStateEntityDiscoveryServicer
from cloudstate.entity_pb2_grpc import add_EntityDiscoveryServicer_to_server
from cloudstate.event_sourced_entity import EventSourcedEntity
from cloudstate.event_sourced_pb2_grpc import add_EventSourcedServicer_to_server
from cloudstate.eventsourced_servicer import CloudStateEventSourcedServicer
from cloudstate.function_pb2_grpc import add_StatelessFunctionServicer_to_server
from cloudstate.function_servicer import CloudStateStatelessFunctionServicer
from cloudstate.stateless_function_entity import StatelessFunction


@dataclass
class CloudState:
    logging.basicConfig(
        format="%(asctime)s - %(filename)s - %(levelname)s: %(message)s",
        level=logging.DEBUG,
    )
    logging.root.setLevel(logging.DEBUG)

    __address: str = ""
    __host = "127.0.0.1"
    __port = "8080"
    __workers = multiprocessing.cpu_count()
    __event_sourced_entities: List[EventSourcedEntity] = field(default_factory=list)
    __stateless_function_entities: List[StatelessFunction] = field(default_factory=list)

    def host(self, address: str):
        """Set the address of the network Host.
        Default Address is 127.0.0.1.
        """
        self.__host = address
        return self

    def port(self, port: str):
        """Set the address of the network Port.
        Default Port is 8080.
        """
        self.__port = port
        return self

    def max_workers(self, workers: Optional[int] = multiprocessing.cpu_count()):
        """Set the gRPC Server number of Workers.
        Default is equal to the number of CPU Cores in the machine.
        """
        self.__workers = workers
        return self

    def register_event_sourced_entity(self, entity: EventSourcedEntity):
        """Registry the user EventSourced entity."""
        self.__event_sourced_entities.append(entity)
        return self

    def register_stateless_function_entity(self, entity: StatelessFunction):
        """Registry the user Stateless Function entity."""
        self.__stateless_function_entities.append(entity)
        return self

    def start(self):
        """Start the user function and gRPC Server."""

        self.__address = "{}:{}".format(
            os.environ.get("HOST", self.__host), os.environ.get("PORT", self.__port)
        )

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.__workers))

        # event sourced
        add_EntityDiscoveryServicer_to_server(
            CloudStateEntityDiscoveryServicer(
                self.__event_sourced_entities, self.__stateless_function_entities
            ),
            server,
        )
        add_EventSourcedServicer_to_server(
            CloudStateEventSourcedServicer(self.__event_sourced_entities), server
        )
        add_StatelessFunctionServicer_to_server(
            CloudStateStatelessFunctionServicer(self.__stateless_function_entities),
            server,
        )
        logging.info("Starting Cloudstate on address %s", self.__address)
        try:
            server.add_insecure_port(self.__address)
            server.start()
        except IOError as e:
            logging.error("Error on start Cloudstate %s", e.__cause__)

        return server
