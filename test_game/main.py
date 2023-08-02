import os
import sys

import pygame

sys.path.append(os.path.dirname(__file__))
from test_game.boring.config import *
import logging

logging.basicConfig(level=logging.INFO, filename="game.log", filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")


def main():
    pygame.init()
    pygame.display.set_caption("Game")
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    from game import Game
    game = Game(win)
    from game import PlantSpot
    PlantSpot.counter = 0
    game.run()
    pygame.quit()


if __name__ == "__main__":
    main()
