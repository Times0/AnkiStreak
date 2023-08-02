import glob
import os

import pygame

if __name__ == "__main__":
    pygame.init()
    win = pygame.display.set_mode((500, 500))

cwd = os.path.dirname(__file__)


def load(path, size=None, vertical_size=None, horizontal_size=None):
    img = pygame.image.load(os.path.join(cwd, "..", "assets", path)).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    elif vertical_size:
        img = pygame.transform.scale(img, (img.get_width() * vertical_size // img.get_height(), vertical_size))
    elif horizontal_size:
        img = pygame.transform.scale(img, (horizontal_size, img.get_height() * horizontal_size // img.get_width()))
    return img


def load_multiple(path):
    l = []
    for p in glob.glob(os.path.join(cwd, "..", "assets", path, "*.png")):
        l.append(pygame.image.load(p).convert_alpha())
    return l


fire_seeds = load("sprites/farm/fire_seeds.png")
water_seeds = load("sprites/farm/water_seeds.png")
ice_seeds = load("sprites/farm/ice_seeds.png")

bucket = load("sprites/farm/bucket.png")
faux = load("sprites/farm/faux.png")

fire_plant = load_multiple("sprites/farm/plants/fire")
water_plant = load_multiple("sprites/farm/plants/water")
ice_plant = load_multiple("sprites/farm/plants/ice")

fire_fruit = load(r"sprites/farm\plants\fruits/fire.png")
water_fruit = load("sprites/farm/plants/fruits/water.png")
ice_fruit = load("sprites/farm/plants/fruits/ice.png")

items = {
    "fire seeds": fire_seeds,
    "water seeds": water_seeds,
    "ice seeds": ice_seeds,

    "fire fruit": fire_fruit,
    "water fruit": water_fruit,
    "ice fruit": ice_fruit,
}

plants = {
    "fire": fire_plant,
    "water": water_plant,
    "ice": ice_plant
}

# _____________________UI___________________________________#
btn_inventory = load("sprites/ui/inventory.png", vertical_size=75)
btn_shop = load("sprites/ui/shop.png", vertical_size=75)
card = load("sprites/ui/anki_card.png")
coin = load("sprites/ui/coin.png")
cross = load("sprites/ui/cross.png")

# make cross black
cross.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
