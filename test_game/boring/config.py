import ctypes
import os

TILE_SIZE = 32

WIDTH, HEIGHT = TILE_SIZE * 45, TILE_SIZE * 30
# dpi awareness
ctypes.windll.user32.SetProcessDPIAware()

FPS = 150
LATE_UPDATE_FPS = 1

MAX_ZOOM = 2
MIN_ZOOM = 1
START_ZOOM = 1.5
ALLOW_SCROLLING = True

MAX_WATERING = 7

cwd = os.path.dirname(__file__)

save_folder = os.path.join(cwd, "..", "game_data")
anki_data_path = os.path.join(cwd, "../..", "anki_data.json")
cards_learned_path = os.path.join(cwd, "../..", "cards_learned_today.txt")
font_path_dir = os.path.join(cwd, "../assets", "fonts")

DEBUG = True
