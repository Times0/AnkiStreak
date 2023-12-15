import os
import sys

from test_game.boring.config import WIDTH, HEIGHT
import logging
import pygame

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.append(os.path.dirname(__file__))

logging.basicConfig(level=logging.INFO, filename="game.log", filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")


def main():
    pygame.init()
    pygame.display.set_caption("AnkiStreak")
    win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE, vsync=True)
    from game import Game
    game = Game(win)
    from game import PlantSpot
    from test_game.backend.tuxemons import Tuxemon
    PlantSpot.counter = 0  # reset class counter (used as id) there is probably a better way to do this
    Tuxemon.counter = 0
    game.run()
    pygame.quit()


if __name__ == "__main__":
    main()
