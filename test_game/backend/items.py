from test_game.backend.objects import GameObjectNoPos
from test_game.boring import imgs


class Item(GameObjectNoPos):
    def __init__(self, name, img):
        super().__init__((50, 50), img)
        self.name = name

    def draw(self, win):
        win.blit(self.zoom_buffer, self.rect)

    def __repr__(self):
        return f"Item({self.name})"


items_data = {
    "fire seeds": Item("fire seeds", imgs.items["fire seeds"]),
    "water seeds": Item("water seeds", imgs.items["water seeds"]),
    "ice seeds": Item("ice seeds", imgs.items["ice seeds"])
}
