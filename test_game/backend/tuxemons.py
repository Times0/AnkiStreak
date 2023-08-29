from enum import Enum

from pygame import Color


class TuxemonType(Enum):
    fire = 1
    water = 2
    ice = 3


all_tuxemons = {"snowrilla": TuxemonType.ice,
                "metesaur": TuxemonType.fire,
                "fribbit": TuxemonType.water}

type_colors: dict[TuxemonType:Color] = {
    TuxemonType.fire: Color("darkred"),
    TuxemonType.water: Color("darkblue"),
    TuxemonType.ice: Color("darkcyan")
}

favorite_fruits: dict[TuxemonType:str] = {
    TuxemonType.fire: "fire fruit",
    TuxemonType.water: "water fruit",
    TuxemonType.ice: "ice fruit"
}


class Tuxemon:
    def __init__(self, name):
        from test_game.boring import imgs

        self.name: str = name
        self.type: TuxemonType = all_tuxemons[name]
        self.xp: int = 1

        self.imgs = imgs.load_tuxemon_imgs(name)

    def max_xp(self):
        return 100

    def __repr__(self):
        return f"Tuxemon({self.name} type: {self.type})"

    def favorite_color(self):
        return type_colors[self.type]

    def add_xp(self, amount):
        self.xp += amount
        if self.xp > self.max_xp():
            self.xp = self.max_xp()
            print(f"{self.name} has reached max xp")

    def favorite_fruit(self):
        return favorite_fruits[self.type]


from test_game.backend.inventory import Inventory


class TuxemonInventory:
    def __init__(self, inventory: Inventory):
        self.tuxemons: dict[str, Tuxemon] = {}
        self.inventory = inventory

    def add_tuxemon(self, t: Tuxemon):
        self.tuxemons[t.name] = t

    def add_default_tuxemons(self):
        for name in all_tuxemons:
            self.add_tuxemon(Tuxemon(name))
        print(self.tuxemons)

    def feed_tuxemon(self, tuxemon_name):
        tuxemon = self.tuxemons.get(tuxemon_name)
        if tuxemon:
            nb_remaining = self.inventory.get(tuxemon.favorite_fruit(), 0)
            if nb_remaining > 0:
                self.inventory.consume_item(tuxemon.favorite_fruit(), 1)
                tuxemon.add_xp(10)

        else:
            print(f"no tuxemon named {tuxemon_name}")

    def dump(self):
        res = {}
        for tuxemon in self.tuxemons.values():
            res[tuxemon.name] = tuxemon.xp
        return res

    def load(self, tuxemons: dict):
        print(self.tuxemons)
        for tuxemon_name in tuxemons:
            tuxemon = Tuxemon(tuxemon_name)
            tuxemon.xp = tuxemons[tuxemon_name]
            self.add_tuxemon(tuxemon)
        print(self.tuxemons)

    def __iter__(self):
        return iter(self.tuxemons.values())
