from cloudstate.cloud_state import CloudState
from shoppingcart.shopping_cart_entity import entity as shopping_cart_entity

if __name__ == '__main__':
    CloudState().register_event_sourced_entity(shopping_cart_entity).serve()
