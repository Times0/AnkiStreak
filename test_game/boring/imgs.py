import glob
import os
from pprint import pprint

import pygame

from test_game.boring.config import font_path_dir

if __name__ == "__main__":
    pygame.init()
    win = pygame.display.set_mode((500, 500))

cwd = os.path.dirname(__file__)


def load_font(name, size):
    font_path = os.path.join(font_path_dir, name)
    print(f"loading font {font_path}")
    return pygame.font.Font(font_path, size)


def load(path, size=None, vertical_size=None, horizontal_size=None):
    img = pygame.image.load(os.path.join(cwd, "..", "assets", path)).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    elif vertical_size:
        img = pygame.transform.scale(img, (img.get_width() * vertical_size // img.get_height(), vertical_size))
    elif horizontal_size:
        img = pygame.transform.scale(img,
                                     (horizontal_size, img.get_height() * horizontal_size // img.get_width()))
    return img


def load_multiple(path):
    l = []
    for p in glob.glob(os.path.join(cwd, "..", "assets", path, "*.png")):
        l.append(pygame.image.load(p).convert_alpha())
    return l


def scale_by(img, scale):
    return pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))


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
btn_tuxemon = load("sprites/ui/tuxemon.png", vertical_size=75)
btn_shop = load("sprites/ui/shop.png", vertical_size=75)
card = load("sprites/ui/anki_card.png")
coin = load("sprites/ui/coin.png")
cross = load("sprites/ui/cross.png")

# make cross black
cross.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)


def load_tuxemon_imgs(name: str) -> dict[str, pygame.Surface]:
    tuxemon_folder = os.path.join(cwd, "..", "assets", "sprites", "tuxemons")
    res = {}
    keys = ["front", "back", "menu01", "menu02"]
    for k in keys:
        file_name = f"{name}-{k}.png"
        res[k] = load(os.path.join(tuxemon_folder, file_name))
    return res


def scale(img, size):
    """Scale image so it fits in a rectangle of size `size`"""
    w, h = size
    w_ratio = w / img.get_width()
    h_ratio = h / img.get_height()
    ratio = min(w_ratio, h_ratio)
    return pygame.transform.scale(img, (int(img.get_width() * ratio), int(img.get_height() * ratio)))


# _____________________NPCs__________________________________#
def load_npc_imgs() -> dict[str, dict[str, pygame.Surface]]:
    WSIZE = 32
    HSIZE = 36
    npc_folder = os.path.join(cwd, "..", "assets", "sprites", "npcs")
    res = {}
    keys = ["back", "right", "front", "left"]

    for filename in os.listdir(npc_folder):
        # each file contains a 4x3 grid of images, top,right,bottom,left. We extract each image
        name = filename.split(".")[0]
        res[name] = {}
        filepath = os.path.join(npc_folder, filename)
        img = load(filepath)
        for k in keys:
            res[name][k] = []
        for i in range(4):
            for j in range(3):
                sprite = img.subsurface(j * WSIZE, i * HSIZE, WSIZE, HSIZE)
                res[name][keys[i]].append(sprite)
    return res


imgs_npc = load_npc_imgs()

if __name__ == '__main__':
    pprint(load_npc_imgs())
