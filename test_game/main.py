import os
import sys

from boring.config import WIDTH, HEIGHT
import logging
import pygame

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.append(os.path.dirname(__file__))

logging.basicConfig(level=logging.INFO, filename="game.log", filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")


def main():
    pygame.init()
    pygame.display.set_caption("Game")
    win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.SCALED)
    from game import Game
    game = Game(win)
    from game import PlantSpot
    PlantSpot.counter = 0  # Avoids starting id counter at 43 when starting a new game without closing the anki window
    game.run()
    pygame.quit()


if __name__ == "__main__":
    main()
