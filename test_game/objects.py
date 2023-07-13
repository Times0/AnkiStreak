import pygame
from utils import clamp
import os
from colors import *
from config import *
import imgs


class PointWithZoom:
    def __init__(self, coords):
        self.coords_init = coords
        self.coords = coords

    def update_camera(self, camera_rect):
        w, h = pygame.display.get_surface().get_size()
        zoom = 1 / (camera_rect.w / w)
        self.coords = (self.coords_init[0] / (camera_rect.w / w) - camera_rect.x * zoom,
                       self.coords_init[1] / (camera_rect.h / h) - camera_rect.y * zoom)


class GameObject_no_img:
    """
    Use pos, don't use rect when using the object
    """
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size
        self.rect = pygame.Rect(pos, size)

    def update_camera(self, camera_rect):
        w, h = pygame.display.get_surface().get_size()
        zoom = 1 / (camera_rect.w / w)
        self.rect.x = self.pos[0] / (camera_rect.w / w) - camera_rect.x * zoom
        self.rect.y = self.pos[1] / (camera_rect.h / h) - camera_rect.y * zoom
        self.rect.width = self.size[0] * zoom
        self.rect.height = self.size[1] * zoom

    def update(self, dt):
        pass


class GameObject_no_pos:
    def __init__(self, size, img):
        self.size = size
        self.img = img
        self.zoom_buffer = self.img
        self.rect = pygame.Rect((0, 0), size)

        if size[0] == -1:
            self.rect.width = self.img.get_width()
        if size[1] == -1:
            self.rect.height = self.img.get_height()

    def update_camera(self, camera_rect):
        w, h = pygame.display.get_surface().get_size()
        zoom = 1 / (camera_rect.w / w)
        self.rect.width = self.size[0] * zoom
        self.rect.height = self.size[1] * zoom
        self.zoom_buffer = pygame.transform.scale(self.img, (int(self.size[0] * zoom), int(self.size[1] * zoom)))

class GameObject(GameObject_no_img):
    def __init__(self, pos, size, img):
        super().__init__(pos, size)
        size = int(size[0]), int(size[1])
        self.size = size
        self.img = pygame.transform.scale(img, size)
        self.zoom_buffer = img

    def update_camera(self, camera_rect):
        GameObject_no_img.update_camera(self, camera_rect)
        w, h = pygame.display.get_surface().get_size()
        zoom = 1 / (camera_rect.w / w)
        self.rect.width = self.size[0] * zoom
        self.rect.height = self.size[1] * zoom
        self.zoom_buffer = pygame.transform.scale(self.img, (int(self.size[0] * zoom), int(self.size[1] * zoom)))

    def draw(self, win):
        win.blit(self.zoom_buffer, self.rect)


class Clickable:
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size
        self.rect = pygame.Rect(pos, size)
        self.hovered = False

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                was_hover = self.hovered
                self.hovered = self.rect.collidepoint(event.pos)
                if self.hovered and not was_hover:
                    self.on_hover()
                elif not self.hovered and was_hover:
                    self.on_hover_end()

    def on_hover(self):
        self.hovered = True
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

    def on_hover_end(self):
        self.hovered = False
        pygame.mouse.set_cursor(*pygame.cursors.arrow)

    def update(self, camera_rect):
        w, h = pygame.display.get_surface().get_size()
        zoom = 1 / (camera_rect.w / w)
        self.rect.width = self.size[0] * zoom
        self.rect.height = self.size[1] * zoom

        self.rect.x = self.pos[0] / (camera_rect.w / w) - camera_rect.x * zoom
        self.rect.y = self.pos[1] / (camera_rect.h / h) - camera_rect.y * zoom

    def draw(self, win):
        if self.hovered:
            pygame.draw.rect(win, RED, self.rect, 2)
        else:
            pygame.draw.rect(win, GREEN, self.rect, 2)


class SortedGroup:
    def __init__(self, *sprites):
        self.sprites = list(sprites)

    def add(self, sprite):
        self.sprites.append(sprite)
        self.sprites.sort(key=lambda x: x.rect.bottom)

    def draw(self, surface):
        for sprite in self.sprites:
            sprite.draw(surface)
