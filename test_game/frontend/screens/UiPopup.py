from test_game.frontend.ui_manager import UIElement
from pygame import Color
import pygame
from pygame.rect import Rect


class Popup(UIElement):
    def __init__(self, text):
        super().__init__("popup", rect=pygame.Rect(0, 0, 300, 200), manager=None)
        self.text = text

    def _draw(self, win):
        pygame.draw.rect(win, Color("white"), self.rect)
        pygame.draw.rect(win, Color("black"), self.rect, 5)
        font = pygame.font.SysFont("Arial", 20, bold=True)
        label = font.render(self.text, True, Color("black"))
        win.blit(label, label.get_rect(center=self.rect.center))
