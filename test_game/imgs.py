import os
import pygame

cwd = os.path.dirname(__file__)


def load(path):
    return pygame.image.load(os.path.join(cwd, "data", path)).convert_alpha()


img_plant1 = load("other/plant.png")
img_plant2 = load("other/plant2.png")
