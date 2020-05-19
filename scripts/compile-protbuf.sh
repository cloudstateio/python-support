#!/usr/bin/env bash

set -o nounset
set -o errexit
set -o pipefail

# follow the basic steps here: https://grpc.io/docs/tutorials/basic/python/

python3 -m grpc_tools.protoc -Iprotobuf/protocol --python_out=. --grpc_python_out=. protobuf/protocol/cloudstate/entity.proto
python3 -m grpc_tools.protoc -Iprotobuf/protocol --python_out=. --grpc_python_out=. protobuf/protocol/cloudstate/event_sourced.proto
python3 -m grpc_tools.protoc -Iprotobuf/frontend --python_out=. --grpc_python_out=. protobuf/frontend/cloudstate/entity_key.proto
python3 -m grpc_tools.protoc -Iprotobuf/example/ -Iprotobuf/frontend --python_out=. --grpc_python_out=. protobuf/example/shoppingcart/shoppingcart.proto
python3 -m grpc_tools.protoc -Iprotobuf/ --python_out=. --grpc_python_out=. protobuf/proxy/grpc/reflection/v1alpha/reflection.proto
python3 -m grpc_tools.protoc -Iprotobuf/ --python_out=. --grpc_python_out=. protobuf/frontend/google/api/annotations.proto
python3 -m grpc_tools.protoc -Iprotobuf/frontend --python_out=. --grpc_python_out=. protobuf/frontend/google/api/annotations.proto
python3 -m grpc_tools.protoc -Iprotobuf/frontend --python_out=. --grpc_python_out=. protobuf/frontend/google/api/http.proto