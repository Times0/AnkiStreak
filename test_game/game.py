import os
import random
import pyscroll
import pygame.sprite
from constants import *
import pytmx

cwd = os.path.dirname(__file__)


class Clickable:
    def __init__(self, pos, size, name):
        print(f"Creating clickable {name}")
        self.pos = pos
        self.size = size
        self.name = name
        self.rect = pygame.Rect(pos, size)

        self.hovered = False
        self.clicked = False

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                pos = event.pos
                if self.rect.collidepoint(pos):
                    self.hovered = True
                    print(f"Hovering over {self.name}")
                else:
                    self.hovered = False

    def draw(self, win):
        pygame.draw.rect(win, RED, self.rect, 2)


class GameObject:
    def __init__(self, pos, size, img):
        self.pos = pos
        self.size = size
        self.img = pygame.transform.scale(img, size)
        self.rect = pygame.Rect(pos, size)

    def draw(self, win):
        win.blit(self.img, self.pos)


class Game:
    def __init__(self, win):
        self.win = win
        self.running = True

        # ______________________TMX and pyscroll_____________________________________#
        self.data_tmx = pytmx.load_pygame("../map.tmx")
        pyscroll_data = pyscroll.data.TiledMapData(self.data_tmx)
        self.map_layer = pyscroll.BufferedRenderer(pyscroll_data, self.win.get_size())
        self.clickable_objects = []
        self.load_objects()
        # _____________________IDK___________________________________#
        self.scrolling = False

    def load_objects(self):
        for obj in self.data_tmx.objects:
            if obj.type == "collision":
                pos = (obj.x, obj.y)
                size = (obj.width, obj.height)
                self.clickable_objects.append(Clickable(pos, size, obj.name))

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            clock.tick(60)
            self.events()
            self.update()
            self.draw()

    def handle_camera_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self.map_layer.zoom += 0.05
                elif event.y < 0:
                    self.map_layer.zoom -= 0.05
                if self.map_layer.zoom < 1:
                    self.map_layer.zoom = 1
                if self.map_layer.zoom > 2:
                    self.map_layer.zoom = 2
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.scrolling = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.scrolling = False

            if event.type == pygame.MOUSEMOTION:
                if self.scrolling:
                    self.map_layer.view_rect.x -= event.rel[0]
                    self.map_layer.view_rect.y -= event.rel[1]

    def events(self):
        events = pygame.event.get()
        self.handle_camera_events(events)
        for obj in self.clickable_objects:
            obj.handle_events(events)

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        pass

    def draw(self):
        self.win.fill(BLACK)
        self.map_layer.center(self.map_layer.view_rect.center)
        self.map_layer.draw(self.win, self.win.get_rect())
        pygame.display.update()
