import os
import pygame
import glob

if __name__ == "__main__":
    pygame.init()
    win = pygame.display.set_mode((500, 500))

cwd = os.path.dirname(__file__)


def load(path):
    return pygame.image.load(os.path.join(cwd, "data", path)).convert_alpha()


def load_multiple(path):
    l = []
    print(os.path.join(cwd, "data", path, "*.png"))
    for p in glob.glob(os.path.join(cwd, "data", path, "*.png")):
        print(p)
        l.append(pygame.image.load(p).convert_alpha())
    return l


empty_plant = load("assets/plant.png")
plant1 = load("assets/plant.png")
plant2 = load("assets/plant2.png")

seeds = load("assets/farm/seeds.png")
fire_seeds = load("assets/farm/fire_seeds.png")
water_seeds = load("assets/farm/water_seeds.png")
ice_seeds = load("assets/farm/ice_seeds.png")

bucket = load("assets/farm/bucket.png")
faux = load("assets/farm/faux.png")

fire_plant = load_multiple("assets/plants/fire")
water_plant = load_multiple("assets/plants/water")
ice_plant = load_multiple("assets/plants/ice")

items = {
    "fire": fire_seeds,
    "water": water_seeds,
    "ice": ice_seeds
}

plants = {
    "fire": fire_plant,
    "water": water_plant,
    "ice": ice_plant
}

# _____________________UI___________________________________#
btn_menu = load("assets/ui/btn_menu.png")
