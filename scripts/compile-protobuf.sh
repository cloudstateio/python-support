#!/usr/bin/env bash

# this script is not needed if you use the setuptools installer; protobuf installation
# to pythonpath will occur if you pip install.

set -o nounset
set -o errexit
set -o pipefail

# follow the basic steps here: https://grpc.io/docs/tutorials/basic/python/
python3 -m grpc_tools.protoc -Iprotobuf/protocol --python_out=${1:-.} --grpc_python_out=${1:-.} ./protobuf/protocol/cloudstate/entity.proto
python3 -m grpc_tools.protoc -Iprotobuf/protocol -Iprotobuf/frontend --python_out=${1:-.} --grpc_python_out=${1:-.} ./protobuf/protocol/cloudstate/crdt.proto

python3 -m grpc_tools.protoc -Iprotobuf/protocol --python_out=${1:-.} --grpc_python_out=${1:-.} ./protobuf/protocol/cloudstate/event_sourced.proto
python3 -m grpc_tools.protoc -Iprotobuf/protocol -Iprotobuf/frontend --python_out=${1:-.} --grpc_python_out=${1:-.} ./protobuf/protocol/cloudstate/function.proto
python3 -m grpc_tools.protoc -Iprotobuf/frontend --python_out=${1:-.} --grpc_python_out=${1:-.} ./protobuf/frontend/cloudstate/entity_key.proto
python3 -m grpc_tools.protoc -Iprotobuf/frontend --python_out=${1:-.} --grpc_python_out=${1:-.} ./protobuf/frontend/cloudstate/eventing.proto

python3 -m grpc_tools.protoc -Iprotobuf/example -Iprotobuf/frontend --python_out=${1:-.} --grpc_python_out=${1:-.} ./protobuf/example/shoppingcart/shoppingcart.proto
python3 -m grpc_tools.protoc -Iprotobuf/example -Iprotobuf/frontend --python_out=${1:-.} --grpc_python_out=${1:-.} ./protobuf/example/shoppingcart/persistence/domain.proto
python3 -m grpc_tools.protoc -Iprotobuf/example -Iprotobuf/frontend --python_out=${1:-.} --grpc_python_out=${1:-.} ./protobuf/example/functiondemo/functiondemo.proto
python3 -m grpc_tools.protoc -Iprotobuf/example -Iprotobuf/frontend --python_out=${1:-.} --grpc_python_out=${1:-.} ./protobuf/example/functiondemo/functiondemo2.proto

# optional
#python3 -m grpc_tools.protoc -Iprotobuf/ --python_out=. --grpc_python_out=. ./protobuf/proxy/grpc/reflection/v1alpha/reflection.proto
#python3 -m grpc_tools.protoc -Iprotobuf/ --python_out=. --grpc_python_out=. protobuf/frontend/google/api/annotations.proto
#python3 -m grpc_tools.protoc -Iprotobuf/frontend --python_out=. --grpc_python_out=. protobuf/frontend/google/api/annotations.proto
#python3 -m grpc_tools.protoc -Iprotobuf/frontend --python_out=. --grpc_python_out=. protobuf/frontend/google/api/http.proto