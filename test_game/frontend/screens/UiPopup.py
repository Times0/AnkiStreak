import pygame
from pygame import Color

from test_game.frontend.ui_manager import UIElement


class Popup(UIElement):
    def __init__(self, text, manager):
        super().__init__("popup", rect=pygame.Rect(0, 0, 500, 200), manager=manager)
        self.text = text

    def _draw(self, win):
        font = pygame.font.SysFont("Arial", 25, bold=True)
        text_surface = font.render(self.text, True, Color("black"))
        win.blit(text_surface, self.rect.topleft)

    def _handle_event(self, event):
        pass
