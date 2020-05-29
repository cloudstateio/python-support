"""
Copyright 2020 Lightbend Inc.
Licensed under the Apache License, Version 2.0.
"""

import platform
from dataclasses import dataclass
from pprint import pprint
from typing import List

from google.protobuf.descriptor_pb2 import FileDescriptorSet, FileDescriptorProto
from google.protobuf.descriptor_pool import Default

from cloudstate import entity_pb2
from cloudstate.entity_pb2_grpc import EntityDiscoveryServicer
from cloudstate.event_sourced_entity import EventSourcedEntity


@dataclass
class CloudStateEntityDiscoveryServicer(EntityDiscoveryServicer):
    event_sourced_entities: List[EventSourcedEntity]

    def discover(self, request, context):
        pprint(request)
        descriptor_set = FileDescriptorSet()
        for entity in self.event_sourced_entities:
            for descriptor in entity.file_descriptors:
                descriptor_set.file.append(FileDescriptorProto.FromString(descriptor.serialized_pb))
        descriptor_set.file.append(
            FileDescriptorProto.FromString(Default().FindFileByName('google/protobuf/empty.proto').serialized_pb)
        )
        descriptor_set.file.append(
            FileDescriptorProto.FromString(Default().FindFileByName('cloudstate/entity_key.proto').serialized_pb)
        )
        descriptor_set.file.append(
            FileDescriptorProto.FromString(Default().FindFileByName('google/protobuf/descriptor.proto').serialized_pb)
        )
        descriptor_set.file.append(
            FileDescriptorProto.FromString(Default().FindFileByName('google/api/annotations.proto').serialized_pb)
        )
        descriptor_set.file.append(
            FileDescriptorProto.FromString(Default().FindFileByName('google/api/http.proto').serialized_pb)
        )
        spec = entity_pb2.EntitySpec(
            service_info=entity_pb2.ServiceInfo(
                service_version='0.1.0',
                service_runtime='Python ' + platform.python_version() + ' [' + platform.python_implementation() + ' ' +
                                platform.python_compiler() + ']',
                support_library_name='cloudstate-python-support',
                support_library_version='0.1.0'
            ),
            entities=[
                entity_pb2.Entity(
                    entity_type=entity.entity_type(),
                    service_name=entity.service_descriptor.full_name,
                    persistence_id=entity.persistence_id,
                )
                for entity in self.event_sourced_entities],
            proto=descriptor_set.SerializeToString()
        )
        return spec

    def reportError(self, request, context):
        pprint(request)
        return
