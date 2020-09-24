"""
Copyright 2020 Lightbend Inc.
Licensed under the Apache License, Version 2.0.
"""

from google.protobuf import symbol_database as _symbol_database
from google.protobuf.any_pb2 import Any

_sym_db = _symbol_database.Default()

TYPE_URL_PREFIX = "type.googleapis.com/"


def get_payload(command):
    command_type: str = command.payload.type_url
    if command_type.startswith(TYPE_URL_PREFIX):
        command_type = command_type[len(TYPE_URL_PREFIX) :]
    command_class = _sym_db.GetSymbol(command_type)
    cmd = command_class()
    cmd.ParseFromString(command.payload.value)
    return cmd


def pack(event):
    any = Any()
    any.Pack(event)
    return any
