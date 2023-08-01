from test_game.game_objects.items import items_data, Item


class ShopItem(Item):
    def __init__(self, price, name, img):
        super().__init__(name, img)
        self.price = price


available_items = {
    "fire seeds": ShopItem(10, "fire seeds", items_data["fire seeds"].img),
    "water seeds": ShopItem(10, "water seeds", items_data["water seeds"].img),
    "ice seeds": ShopItem(10, "ice seeds", items_data["ice seeds"].img)
}


class Shop:
    """
    A shopUI is a collection of items that can be bought, they are stored in a dictionary
    With name
    """

    def __init__(self):
        self.items = available_items
