from boring import imgs
from backend.items import Item


class Inventory:
    def __init__(self):
        self.items = {}  # name: quantity
        self.items_data: dict[str, Item] = {}  # name: Item

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

    def get_image(self, item_name):
        return self.items_data[item_name].img

    def __getitem__(self, item_name):
        return self.items[item_name]

    def __setitem__(self, item_name, value):
        self.items[item_name] = value

    def __contains__(self, item: Item):
        return item.name in self.items

    def __iter__(self):
        return iter(self.items)

    def __repr__(self):
        return f"Inventory({self.items})"

    def consume_item(self, name, nb):
        if name in self.items:
            self.items[name] -= nb
            if self.items[name] == 0:
                del self.items[name]
        else:
            raise Exception(f"Item not found in inventory \n "
                            f"{name} not in {self.items}")
