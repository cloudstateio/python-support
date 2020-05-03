from cloudstate.event_sourced_entity import EventSourcedEntity
from shoppingcart.shoppingcart_pb2 import (_SHOPPINGCART,DESCRIPTOR as FILE_DESCRIPTOR)


entity = EventSourcedEntity(_SHOPPINGCART,[FILE_DESCRIPTOR])
