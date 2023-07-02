import os
import pygame

cwd = os.path.dirname(__file__)


def load(path):
    return pygame.image.load(os.path.join(cwd, "data", path)).convert_alpha()


empty_plant = load("other/plant.png")
plant1 = load("other/plant.png")
plant2 = load("other/plant2.png")

seeds = load("other/farm/seeds.png")
bucket = load("other/farm/bucket.png")
faux = load("other/farm/faux.png")
