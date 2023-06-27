import ctypes

WIDTH, HEIGHT = 32 * 45, 32 * 30
# dpi awareness
ctypes.windll.user32.SetProcessDPIAware()

FPS = 60
MAX_ZOOM = 2
MIN_ZOOM = 1
ALLOW_SCROOLING = True
