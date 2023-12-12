import pygame


class Hoverable:
    def __init__(self, rect: pygame.Rect, inflate=10):
        self.hovered = False
        self.rect = rect
        self.inflate = inflate

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos) and not self.hovered:
                self.on_hover()
            elif not self.rect.collidepoint(event.pos) and self.hovered:
                self.on_unhover()

    def on_hover(self):
        self.hovered = True
        self.rect = self.rect.inflate(self.inflate, self.inflate)

    def on_unhover(self):
        self.hovered = False
        self.rect = self.rect.inflate(-self.inflate, -self.inflate)
