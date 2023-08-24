from typing import Optional

import pygame
from PygameUIKit.button import ButtonPngIcon
from pygame import Color
from pygame import Rect

from test_game.boring import imgs

cross_btn = pygame.transform.scale(imgs.cross, (50, 50))

debug = True


class UIElement:
    def __init__(self, name, rect: Rect, manager):
        self.name: str = name
        self.manager: UIManager = manager
        self.rect: Rect = rect
        self.active: bool = False
        self.visible: bool = False

        self.btn_close = ButtonPngIcon(cross_btn, Color("red"), self.close, opacity=0.9)

    def _handle_event(self, event):
        raise NotImplementedError

    def handle_event(self, event):
        self._handle_event(event)
        self.btn_close.handle_event(event)

    def _draw(self, win):
        raise NotImplementedError

    def draw(self, win):
        self._draw(win)
        if debug:
            pygame.draw.rect(win, Color("red"), self.rect, 2)
        self.btn_close.draw(win, *self.btn_close.image.get_rect(bottomright=self.rect.topright).topleft)

    def close(self):
        self.manager.active_element = None


class UIManager:
    def __init__(self, elements=None):
        if elements is None:
            elements = []

        self.elements: dict[str, UIElement] = {element.name: element for element in elements}
        self.active_element: Optional[UIElement] = None

    def add_elements(self, elements: list[UIElement]):
        for element in elements:
            self.elements[element.name] = element

    def open(self, name):
        self.active_element = self.elements[name]

    def draw(self, win):
        if self.active_element:
            self.active_element.draw(win)

    def handle_event(self, event):
        if self.active_element:
            self.active_element.handle_event(event)
