import pygame

from test_game.boring import imgs
from test_game.game_objects.items import Item


class Inventory:
    def __init__(self):
        self.items = {}  # name: quantity
        self.items_data = {}  # name: Item

    def add_item(self, item: Item):
        if item.name in self.items:
            self.items[item.name] += 1
        else:
            self.items[item.name] = 1
            self.items_data[item.name] = item

    def remove_item(self, item):
        if item.name in self.items:
            self.items[item.name] -= 1
            if self.items[item.name] == 0:
                del self.items[item.name]
        else:
            raise Exception("Item not found in inventory")

    def dump(self) -> dict:
        return self.items

    def load(self, items: dict):
        self.items = items
        for item_name in items:
            self.items_data[item_name] = Item(item_name, imgs.items[item_name])

    def __getitem__(self, item_name):
        return self.items[item_name]

    def __setitem__(self, item_name, value):
        self.items[item_name] = value

    def __contains__(self, item_name):
        return item_name in self.items

    def __iter__(self):
        return iter(self.items)

    def get_item_image(self, item_name) -> pygame.Surface:
        return self.items_data[item_name].img
