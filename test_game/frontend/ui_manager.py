from typing import Optional

import pygame
from PygameUIKit.button import ButtonPngIcon
from pygame import Color
from pygame import Rect

from test_game.boring import imgs
from test_game.frontend.utils import blit_acrylic_surface

cross_btn = pygame.transform.scale(imgs.cross, (50, 50))

debug = False


class AcrylicBackground:
    def __init__(self):
        self.surface = None
        self.require_update = True
        self.acrylic_surface = None
        self.acrylic_surface_rect = None

    def render(self, screen_in, rect, blur_radius, color=Color(220, 200, 200, 128)):
        self.acrylic_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        self.acrylic_surface_rect = self.acrylic_surface.get_rect(topleft=rect.topleft)
        surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        surface.fill(color)
        blit_acrylic_surface(screen_in, self.acrylic_surface, rect.topleft, surface, blur_radius=blur_radius)
        self.require_update = False

    def draw_acrylic_background(self, win, rect, blur_radius=5):
        if self.require_update:
            self.surface = pygame.Surface(rect.size, pygame.SRCALPHA)
            self.render(win, rect, blur_radius=blur_radius)
            self.require_update = False

        win.blit(self.acrylic_surface, self.acrylic_surface_rect)


class UIElement(AcrylicBackground):
    def __init__(self, name, manager, rect: Rect = Rect(0, 0, 0, 0), is_permament=False):
        super().__init__()
        self.name: str = name
        self.manager: UIManager = manager
        self.rect: Rect = rect
        if rect.x == 0 and rect.y == 0:
            self.rect.center = (self.manager.rect.width // 2, self.manager.rect.height // 2)
        self.active: bool = False
        self.visible: bool = False

        self.is_permament = is_permament
        if not is_permament:
            self.btn_close: Optional[ButtonPngIcon] = None
            self.instantiate_button_cross()

    def instantiate_button_cross(self):
        self.btn_close = ButtonPngIcon(cross_btn,
                                       onclick_f=self.close,
                                       hover_color=Color((181, 200, 71)),
                                       opacity=1,
                                       inflate=0)

    def _handle_event(self, event):
        print(f"{self.name}")
        raise NotImplementedError

    def handle_event(self, event):
        self._handle_event(event)
        if self.is_permament:
            return
        self.btn_close.handle_event(event)

    def _update(self, dt):
        pass

    def update(self, dt):
        if self.is_permament:
            self._update(dt)
            return
        self._update(dt)

    def _draw(self, win):
        raise NotImplementedError

    def draw(self, win):
        if self.is_permament:
            self._draw(win)
            return
        self.draw_window(win)
        self._draw(win)
        self.btn_close.draw(win, *self.btn_close.image.get_rect(bottomright=self.rect.topright).topleft)

    def draw_window(self, win):
        self.draw_acrylic_background(win, self.rect, blur_radius=15)
        pygame.draw.rect(win, Color("black"), self.rect, 5, border_radius=10)

    def _close(self):
        pass

    def close(self):
        self._close()
        self.require_update = True
        self.manager.active_element = None


class UIManager:
    from test_game.frontend.screens.UiPopup import Popup
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.active_element.close()
                    return
            self.active_element.handle_event(event)

        else:
            for element in self.perma_elements.values():
                element.handle_event(event)

    def update(self, dt):
        if self.active_element:
            self.active_element.update(dt)

        for element in self.perma_elements.values():
            element.update(dt)

    def add_popop(self, popup: Popup):
        self.elements[popup.name] = popup
        self.open(popup.name)
