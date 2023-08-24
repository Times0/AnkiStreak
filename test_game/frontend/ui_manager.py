from typing import Optional

import pygame
from PygameUIKit.button import ButtonPngIcon
from pygame import Color
from pygame import Rect

from test_game.boring import imgs

cross_btn = pygame.transform.scale(imgs.cross, (50, 50))

debug = True


class UIElement:
    def __init__(self, name, manager, rect: Rect = Rect(0, 0, 0, 0), is_permament=False):
        self.name: str = name
        self.manager: UIManager = manager
        self.rect: Rect = rect
        if rect.x == 0 and rect.y == 0:
            self.rect.center = (self.manager.rect.width // 2, self.manager.rect.height // 2)
        self.active: bool = False
        self.visible: bool = False

        self.is_permament = is_permament
        if not is_permament:
            self.btn_close = ButtonPngIcon(cross_btn, Color("red"), self.close, opacity=0.9)

    def _handle_event(self, event):
        print(f"{self.name}")
        raise NotImplementedError

    def handle_event(self, event):
        self._handle_event(event)
        if self.is_permament:
            return
        self.btn_close.handle_event(event)

    def _draw(self, win):
        raise NotImplementedError

    def draw(self, win):
        self._draw(win)
        if self.is_permament:
            return
        if debug:
            pygame.draw.rect(win, Color("red"), self.rect, 2)

        self.btn_close.draw(win, *self.btn_close.image.get_rect(bottomright=self.rect.topright).topleft)

    def close(self):
        self.manager.active_element = None


class UIManager:
    def __init__(self, elements=None):
        self.elements: dict[str, UIElement] = {}
        self.perma_elements: dict[str, UIElement] = {}

        self.add_elements(elements)
        self.active_element: Optional[UIElement] = None

        self.rect = pygame.display.get_surface().get_rect()

    def add_elements(self, elements: list[UIElement]):
        if elements is None:
            return
        for element in elements:
            if element.is_permament:
                self.perma_elements[element.name] = element
            else:
                self.elements[element.name] = element

    def open(self, name):
        self.active_element = self.elements[name]

    def draw(self, win):
        for element in self.perma_elements.values():
            element.draw(win)

        if self.active_element:
            self.active_element.draw(win)

    def handle_event(self, event):
        if self.active_element:
            self.active_element.handle_event(event)
        else:
            for element in self.perma_elements.values():
                element.handle_event(event)
