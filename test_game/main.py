import os
import sys

from test_game.boring.config import WIDTH, HEIGHT
import logging
import pygame

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.append(os.path.dirname(__file__))

logging.basicConfig(level=logging.INFO, filename="game.log", filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")

r"""
Anki 23.12.1 (1a1d4d54)  (ao)
Python 3.9.15 Qt 6.6.1 PyQt 6.6.1
Platform: Windows-10-10.0.22621

Traceback (most recent call last):
  File "aqt.progress", line 118, in handler
  File "aqt.main", line 218, in on_window_init
  File "aqt.main", line 265, in setupProfileAfterWebviewsLoaded
  File "aqt.main", line 317, in setupProfile
  File "aqt.main", line 496, in loadProfile
  File "_aqt.hooks", line 4101, in __call__
  File "C:\Users\spoto\AppData\Roaming\Anki2\addons21\ankistreak_test\__init__.py", line 43, in on_profile_open
    start_game()
  File "C:\Users\spoto\AppData\Roaming\Anki2\addons21\ankistreak_test\__init__.py", line 34, in start_game
    test_game.main.main()
  File "C:\Users\spoto\AppData\Roaming\Anki2\addons21\ankistreak_test\test_game\main.py", line 19, in main
    icon = pygame.image.load(os.path.join("assets", "sprites", "ui", "tuxemon_border.png"))
FileNotFoundError: No file 'assets\sprites\ui\tuxemon_border.png' found in working directory 'C:\Users\spoto\AppData\Local\Programs\Anki'.

===Add-ons (active)===
(add-on provided name [Add-on folder, installed at, version, is config changed])
'' ['ankistreak_test', 0, 'None', '']

===IDs of active AnkiWeb add-ons===


===Add-ons (inactive)===
(add-on provided name [Add-on folder, installed at, version, is config changed])


"""
def main():
    pygame.init()
    pygame.display.set_caption("AnkiStreak")
    # set the window icon
    cwd = os.path.dirname(__file__)
    icon = pygame.image.load(os.path.join(cwd,"assets", "sprites", "ui", "tuxemon_border.png"))
    pygame.display.set_icon(icon)
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
