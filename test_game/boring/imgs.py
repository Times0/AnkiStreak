import glob
import os

import pygame

if __name__ == "__main__":
    pygame.init()
    win = pygame.display.set_mode((500, 500))

cwd = os.path.dirname(__file__)


def load(path, size=None, vertical_size=None, horizontal_size=None):
    img = pygame.image.load(os.path.join(cwd, "..", "data", path)).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    elif vertical_size:
        img = pygame.transform.scale(img, (img.get_width() * vertical_size // img.get_height(), vertical_size))
    elif horizontal_size:
        img = pygame.transform.scale(img, (horizontal_size, img.get_height() * horizontal_size // img.get_width()))
    return img


def load_multiple(path):
    l = []
    for p in glob.glob(os.path.join(cwd, "..", "data", path, "*.png")):
        l.append(pygame.image.load(p).convert_alpha())
    return l


fire_seeds = load("assets/farm/fire_seeds.png")
water_seeds = load("assets/farm/water_seeds.png")
ice_seeds = load("assets/farm/ice_seeds.png")

bucket = load("assets/farm/bucket.png")
faux = load("assets/farm/faux.png")

fire_plant = load_multiple("assets/plants/fire")
water_plant = load_multiple("assets/plants/water")
ice_plant = load_multiple("assets/plants/ice")

items = {
    "fire seeds": fire_seeds,
    "water seeds": water_seeds,
    "ice seeds": ice_seeds
}

plants = {
    "fire": fire_plant,
    "water": water_plant,
    "ice": ice_plant
}

# _____________________UI___________________________________#
btn_inventory = load("assets/ui/inventory.png", vertical_size=75)
btn_shop = load("assets/ui/shop.png", vertical_size=75)
card = load("assets/ui/anki_card.png")
