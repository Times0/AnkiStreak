import pygame
from pygame import Surface, Rect, Color

from enum import Enum, auto
from test_game.backend.objects import GameObjectNoPos
from test_game.frontend.utils import draw_transparent_rect


class TuxemonType:
    fire = 1
    water = 2
    ice = 3


all_tuxemons = {"snowrilla": TuxemonType.ice,
                "metesaur": TuxemonType.fire,
                "velocitile": TuxemonType.water}
type_colors: dict[TuxemonType:Color] = {
    TuxemonType.fire: Color("darkred"),
    TuxemonType.water: Color("darkblue"),
    TuxemonType.ice: Color("darkcyan")
}


class Tuxemon:
    def __init__(self, name):
        from test_game.boring import imgs

        self.name: str = name
        self.type: TuxemonType = all_tuxemons[name]
        self.xp: int = 50

        self.imgs = imgs.load_tuxemon_imgs(name)

    def max_xp(self):
        return 100

    def __repr__(self):
        return f"Tuxemon({self.name} type: {self.type})"

    def favorite_color(self):
        return type_colors[self.type]


class TuxemonInventory:
    def __init__(self):
        self.tuxemons: list[Tuxemon] = []

    def add_tuxemon(self, t: Tuxemon):
        self.tuxemons.append(t)

    def remove_tuxemon(self, t: Tuxemon):
        self.tuxemons.remove(t)

    def add_default_tuxemons(self):
        for name in all_tuxemons:
            self.add_tuxemon(Tuxemon(name))
        print(self.tuxemons)


if __name__ == '__main__':
    from test_game.frontend.screens import TuxemonCard

    pygame.init()
    pygame.display.set_mode((500, 500))

    tuxemon_inventory = TuxemonInventory()
    tuxemon_inventory.add_default_tuxemons()

    cards = []
    for i, tuxemon in enumerate(tuxemon_inventory.tuxemons):
        card = TuxemonCard(tuxemon, Rect(0, 0, 80, 80))
        cards.append(card)

    clock = pygame.time.Clock()
    while 1:
        dt = clock.tick(500) / 1000
        print(f"\rfps: {clock.get_fps()}", end="")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
        for i, card in enumerate(cards):
            card.update(dt)
            card.draw(pygame.display.get_surface(), (i * 100 + 50, 50))
        pygame.display.update()
