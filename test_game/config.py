import ctypes
TILE_SIZE = 32

WIDTH, HEIGHT = TILE_SIZE * 45, TILE_SIZE * 30
# dpi awareness
ctypes.windll.user32.SetProcessDPIAware()

FPS = 60
MAX_ZOOM = 2
MIN_ZOOM = 1
ALLOW_SCROOLING = True
