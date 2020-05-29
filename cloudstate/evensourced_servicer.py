"""
Copyright 2020 Lightbend Inc.
Licensed under the Apache License, Version 2.0.
"""

import logging
from pprint import pprint
from typing import List

from google.protobuf import symbol_database as _symbol_database
from google.protobuf.any_pb2 import Any

from cloudstate.entity_pb2 import Command
from cloudstate.event_sourced_context import SnapshotContext, EventSourcedCommandContext, EventContext
from cloudstate.event_sourced_entity import EventSourcedEntity, EventSourcedHandler
from cloudstate.event_sourced_pb2 import EventSourcedInit, EventSourcedSnapshot, EventSourcedEvent, EventSourcedReply, \
    EventSourcedStreamOut
from cloudstate.event_sourced_pb2_grpc import EventSourcedServicer

_sym_db = _symbol_database.Default()

TYPE_URL_PREFIX = 'type.googleapis.com/'


def get_payload(command):
    command_type: str = command.payload.type_url
    if command_type.startswith(TYPE_URL_PREFIX):
        command_type = command_type[len(TYPE_URL_PREFIX):]
    command_class = _sym_db.GetSymbol(command_type)
    cmd = command_class()
    cmd.ParseFromString(command.payload.value)
    return cmd


def pack(event):
    any = Any()
    any.Pack(event)
    return any


class CloudStateEventSourcedServicer(EventSourcedServicer):
    def __init__(self,event_sourced_entities: List[EventSourcedEntity]):
        self.event_sourced_entities = { entity.name():entity for entity in event_sourced_entities}

    def handle(self, request_iterator, context):
        initiated = False
        current_state = None
        handler:EventSourcedHandler = None
        entity_id:str = None
        start_sequence_number:int =0
        for request in request_iterator:
            if not initiated:
                if request.HasField("init"):
                    init:EventSourcedInit = request.init
                    service_name = init.service_name
                    entity_id = init.entity_id
                    if not service_name in self.event_sourced_entities:
                        raise Exception("No event sourced entity registered for service {}".format(service_name))
                    entity = self.event_sourced_entities[service_name]
                    handler = EventSourcedHandler(entity)
                    current_state = handler.init_state(entity_id)
                    initiated = True
                    if init.HasField('snapshot'):
                        event_sourced_snapshot:EventSourcedSnapshot= init.snapshot
                        start_sequence_number = event_sourced_snapshot.snapshot_sequence
                        snapshot = get_payload(event_sourced_snapshot.snapshot)
                        snapshot_context = SnapshotContext(entity_id,start_sequence_number)
                        snapshot_result = handler.handle_snapshot(current_state,snapshot,snapshot_context)
                        if snapshot_result:
                            current_state = snapshot_result
                else:
                    raise Exception("Cannot handle {} before initialization".format(request))

            elif request.HasField('event'):
                event:EventSourcedEvent = request.event
                evt = get_payload(event)
                event_result = handler.handle_event(current_state, evt,
                                                    EventContext(entity_id, event.sequence))
                start_sequence_number = event.sequence
                if event_result:
                    current_state = event_result
                pprint("Handling event {}".format(event))
            elif request.HasField('command'):
                command:Command = request.command
                cmd = get_payload(command)
                ctx = EventSourcedCommandContext(command.name,command.id,entity_id,start_sequence_number)
                result = None
                try:
                    result = handler.handle_command(current_state,cmd,ctx)
                except Exception as ex:
                    ctx.fail(str(ex))
                    logging.exception('Failed to execute command:'+str(ex))

                client_action = ctx.create_client_action(result, False)
                event_sourced_reply = EventSourcedReply()
                event_sourced_reply.command_id = command.id
                event_sourced_reply.client_action.CopyFrom(client_action)
                snapshot = None
                perform_snapshot=False
                if not ctx.has_errors():
                    for number, event in enumerate(ctx.events):
                        sequence_number = start_sequence_number+number+1
                        event_result = handler.handle_event(current_state,event,EventContext(entity_id,start_sequence_number+number))
                        if event_result:
                            current_state = event_result
                        snapshot_every=handler.entity.snapshot_every
                        perform_snapshot = (snapshot_every > 0) and (
                                perform_snapshot or (sequence_number % snapshot_every == 0))
                    end_sequence_number = start_sequence_number + len(ctx.events)
                    if perform_snapshot:
                        snapshot = handler.snapshot(current_state,SnapshotContext(entity_id,end_sequence_number))

                    event_sourced_reply.side_effects.extend(ctx.effects)
                    event_sourced_reply.events.extend([pack(event)  for event in ctx.events])
                    if snapshot:
                        event_sourced_reply.snapshot.Pack(snapshot)

                output = EventSourcedStreamOut()
                output.reply.CopyFrom(event_sourced_reply)
                yield output

            else:
                raise Exception("Cannot handle {} after initialization".format(type(request)))


