import pygame


class Hoverable:
    def __init__(self, rect: pygame.Rect, inflate=10):
        self.hovered = False
        self.rect_default = rect
        self.rect_inflated = rect.inflate(inflate, inflate)
        self.rect = rect

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:

            if self.rect.collidepoint(event.pos):
                self.on_hover()
            else:
                self.on_unhover()

    def on_hover(self):
        self.hovered = True
        self.rect = self.rect_inflated

    def on_unhover(self):
        self.hovered = False
        self.rect = self.rect_default
