import random
from pprint import pprint
from typing import Optional

import pygame
from pygame import Vector2

from test_game.backend.objects import GameObject
from test_game.boring import config
from test_game.boring.config import WIDTH, HEIGHT
from test_game.boring.imgs import imgs_npc, scale_by

ANIM_PER_SEC = 4
NPC_SPEED = 50


class NPC:
    def __init__(self, name, path):
        self.og_imgs: dict[str, list[pygame.Surface]] = imgs_npc[name]
        self.current_imgs: dict[str, list[pygame.Surface]] = self.og_imgs
        self.imgs_cache: dict[float, dict[str, list[pygame.Surface]]] = {}
        self.direction_str = "front"  # "front", "back", "left", "right"
        self.anim_index = 0

        self.size = (32, 36)

        self.target: Optional[tuple[int, int]] = None
        self.direction: Optional[Vector2] = None
        self.speed = NPC_SPEED
        self.path = path
        self.path_index = random.randint(1, len(path) - 2)
        self.pos = Vector2(path[self.path_index])
        self.rect = pygame.Rect(self.pos, self.size)
        self.anim_timer = 0

    def update_camera(self, camera_rect):
        zoom = 1 / (camera_rect.w / WIDTH)
        self.rect.x = self.pos[0] / (camera_rect.w / WIDTH) - camera_rect.x * zoom
        self.rect.y = self.pos[1] / (camera_rect.h / HEIGHT) - camera_rect.y * zoom
        if zoom not in self.imgs_cache:
            self.imgs_cache[zoom] = {}
            for k, imgs in self.og_imgs.items():
                self.imgs_cache[zoom][k] = [
                    pygame.transform.scale(img, (int(self.size[0] * zoom), int(self.size[1] * zoom))) for img in imgs]
        self.current_imgs = self.imgs_cache[zoom]
        self.rect = self.current_imgs[self.direction_str][self.anim_index].get_rect(center=self.rect.topleft)

    def update(self, dt):
        if not self.target:
            self.path_index += 1
            self.target = self.path[self.path_index]
            if self.path_index >= len(self.path) - 1:
                self.path_index = 0
        else:
            self.move(dt)
        self.animate(dt)

    def animate(self, dt):
        self.anim_timer += dt
        if self.anim_timer >= 1 / ANIM_PER_SEC:
            self.anim_timer = 0
            self.anim_index += 1
            if self.anim_index >= len(self.og_imgs[self.direction_str]):
                self.anim_index = 0

    def compute_direction(self):
        self.direction = Vector2(self.target) - self.pos
        self.direction.normalize_ip()
        if abs(self.direction.x) > abs(self.direction.y):
            if self.direction.x > 0:
                self.direction_str = "right"
            else:
                self.direction_str = "left"
        else:
            if self.direction.y > 0:
                self.direction_str = "front"
            else:
                self.direction_str = "back"

    def move(self, dt):
        if self.direction is None:
            self.compute_direction()
        step_size = self.speed * dt
        distance_to_target = Vector2(self.target) - self.pos
        if distance_to_target.length() <= step_size:
            self.pos = Vector2(self.target)
            self.target = None
            self.direction = None
        else:
            self.pos += self.direction * step_size

    def draw(self, win):
        img = self.current_imgs[self.direction_str][self.anim_index]
        win.blit(img, self.rect)
        if config.DEBUG:
            pygame.draw.rect(win, pygame.Color("red"), self.rect, 1)
