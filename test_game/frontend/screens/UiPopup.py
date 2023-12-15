import pygame
from pygame import Color

from test_game.frontend.ui_manager import UIElement


class Popup(UIElement):
    def __init__(self, title, text, manager):
        super().__init__("popup", rect=pygame.Rect(0, 0, 500, 200), manager=manager)
        self.title = title
        self.text = text

        self._texts = self.text.split("\n")

        self.title_font = pygame.font.SysFont("Arial", 30, bold=True)
        self.font = pygame.font.SysFont("Arial", 20)

    def _draw(self, win):
        pygame.draw.rect(win, Color("black"), self.rect, 5)

        title = self.title_font.render(self.title, True, Color("black"))
        win.blit(title, title.get_rect(center=(self.rect.centerx, self.rect.top + 20)))

        for i, text in enumerate(self._texts):
            text = self.font.render(text, True, Color("black"))
            win.blit(text, text.get_rect(center=(self.rect.centerx, self.rect.top + 60 + i * 30)))

    def _handle_event(self, event):
        pass
