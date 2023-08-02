from test_game.backend.inventory import Inventory
from test_game.backend.items import items_data, Item


class ShopItem(Item):
    def __init__(self, price, name, img):
        super().__init__(name, img)
        self.price = price


available_items = {
    "fire seeds": ShopItem(10, "fire seeds", items_data["fire seeds"].img),
    "water seeds": ShopItem(10, "water seeds", items_data["water seeds"].img),
    "ice seeds": ShopItem(10, "ice seeds", items_data["ice seeds"].img)
}


class Wallet:
    def __init__(self, ui=None, money=0):
        self.money = money
        self.ui = ui
        if self.ui:
            self.ui.update_money(self.money)

    def link_ui(self, ui):
        self.ui = ui
        self.ui.update_money(self.money)

    def spend_money(self, amount):
        self.money -= amount
        self.ui.update_money(self.money)

    def gain_money(self, amount):
        self.money += amount
        self.ui.update_money(self.money)

    def dump(self):
        return self.money

    def load(self, money):
        self.money = money
        self.ui.update_money(self.money)


class Shop:
    def __init__(self, wallet: Wallet, inventory: Inventory):
        self.items = available_items
        self.wallet = wallet
        self.inventory = inventory

    def buy(self, item: ShopItem):
        if self.wallet.money >= item.price:
            self.wallet.spend_money(item.price)
            self.inventory.add_item(item)
            print(f"bought {item} for {item.price}, you have {self.wallet.money} left")

        else:
            print("not enough money")
