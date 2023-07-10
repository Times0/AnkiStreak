import ctypes
import os

TILE_SIZE = 32

WIDTH, HEIGHT = TILE_SIZE * 45, TILE_SIZE * 30
# dpi awareness
ctypes.windll.user32.SetProcessDPIAware()

FPS = 60
MAX_ZOOM = 2
MIN_ZOOM = 1
ALLOW_SCROOLING = True

cwd = os.path.dirname(__file__)
save_path = os.path.join(cwd, "data", "game_data", "game_state.json")
