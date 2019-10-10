# Copyright 2019 Lightbend Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import platform
from concurrent import futures
from pprint import pprint

import grpc
from google.protobuf.descriptor_pb2 import FileDescriptorSet, FileDescriptorProto
from google.protobuf.descriptor_pool import Default

from cloudstate import entity_pb2
from cloudstate.entity_pb2_grpc import add_EntityDiscoveryServicer_to_server, EntityDiscoveryServicer
from shoppingcart import shoppingcart_pb2

EVENT_SOURCED = 'cloudstate.eventsourced.EventSourced'


class CloudStateEntityDiscoveryServicer(EntityDiscoveryServicer):
    def discover(self, request, context):
        pprint(request)
        descriptor_set = FileDescriptorSet()
        descriptor_set.file.append(FileDescriptorProto.FromString(shoppingcart_pb2.DESCRIPTOR.serialized_pb))
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
                service_name='shopping-cart',
                service_version='0.1.0',
                service_runtime='Python ' + platform.python_version() + ' [' + platform.python_implementation() + ' ' + platform.python_compiler() + ']',
                support_library_name='cloudstate-python-support',
                support_library_version='0.1.0'
            ),
            entities=[
                entity_pb2.Entity(
                    entity_type=EVENT_SOURCED,
                    service_name='com.example.shoppingcart.ShoppingCart',
                    persistence_id='shopping_cart',
                )
            ],
            proto=descriptor_set.SerializeToString()
        )
        return spec

    def reportError(self, request, context):
        pprint(request)
        return


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_EntityDiscoveryServicer_to_server(CloudStateEntityDiscoveryServicer(), server)
    port = os.environ.get('HOST', '127.0.0.1') + ':' + os.environ.get('PORT', '50051')
    server.add_insecure_port(port)
    pprint('Starting CloudStateEntityDiscoveryServicer on ' + port)
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
