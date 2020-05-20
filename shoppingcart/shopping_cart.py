from cloudstate.cloudstate import CloudState
from shoppingcart.shopping_cart_entity import entity as shopping_cart_entity
import logging

if __name__ == '__main__':
    logging.basicConfig()
    CloudState().register_event_sourced_entity(shopping_cart_entity).start()
