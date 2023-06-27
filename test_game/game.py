import os
from colors import *
import pyscroll
import pygame.sprite
from config import *
import pytmx

cwd = os.path.dirname(__file__)


class GameObject:
    def __init__(self, pos, size, img):
        self.pos = pos
        self.size = size
        self.img = pygame.transform.scale(img, size)
        self.rect = pygame.Rect(pos, size)

        self.zoom_buffer = img

    def update(self, camera_rect):
        w, h = pygame.display.get_surface().get_size()
        zoom = 1 / (camera_rect.w / w)
        self.rect.width = self.size[0] * zoom
        self.rect.height = self.size[1] * zoom

        self.rect.x = self.pos[0] / (camera_rect.w / w) - camera_rect.x * zoom
        self.rect.y = self.pos[1] / (camera_rect.h / h) - camera_rect.y * zoom

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


class Farm(GameObject, Clickable):
    def __init__(self, pos, size, img):
        GameObject.__init__(self, pos, size, img)
        Clickable.__init__(self, pos, size)
        self.menu_open = False

    def handle_events(self, events):
        Clickable.handle_events(self, events)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.menu_open = False
                if self.hovered:
                    self.menu_open = True

    def draw(self, win):
        GameObject.draw(self, win)
        if self.menu_open:
            pygame.draw.rect(win, RED, self.rect, 2)


class SortedGroup:
    def __init__(self, *sprites):
        self.sprites = list(sprites)

    def add(self, sprite):
        self.sprites.append(sprite)
        self.sprites.sort(key=lambda x: x.rect.bottom)

    def draw(self, surface):
        for sprite in self.sprites:
            sprite.draw(surface)


class Game:
    def __init__(self, win):
        self.win = win
        self.running = True

        # ______________________TMX and pyscroll_____________________________________#
        self.data_tmx = pytmx.load_pygame(os.path.join(cwd, "data", "map_with_objects.tmx"))
        pyscroll_data = pyscroll.data.TiledMapData(self.data_tmx)
        self.map_layer = pyscroll.BufferedRenderer(pyscroll_data, self.win.get_size(), clamp_camera=True)
        self.clickable_objects = []
        self.objects = SortedGroup()
        self.load_objects()

        # _____________________IDK___________________________________#
        self.scrolling = False
        self.map_layer.zoom = 2
        self.zoom_target = self.map_layer.zoom

    def load_objects(self):
        for obj in self.data_tmx.objects:
            if obj.type == "collision":
                pos = (obj.x, obj.y)
                size = (obj.width, obj.height)
                self.clickable_objects.append(Clickable(pos, size))
            elif obj.type == "Farm":
                pos = (obj.x, obj.y)
                size = (obj.width, obj.height)
                img = obj.image
                o = Farm(pos, size, img)
                self.clickable_objects.append(o)
                self.objects.add(o)
            else:
                pos = (obj.x, obj.y)
                size = (obj.width, obj.height)
                img = obj.image
                self.objects.add(GameObject(pos, size, img))

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            clock.tick(FPS)
            print(f"\r{clock.get_fps()}", end="")
            self.events()
            self.update()
            self.draw()

    def handle_camera_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEWHEEL and ALLOW_SCROOLING:
                if event.y > 0:
                    self.zoom_target += 0.05
                elif event.y < 0:
                    self.zoom_target -= 0.05
                if self.zoom_target < MIN_ZOOM:
                    self.zoom_target = MIN_ZOOM
                if self.zoom_target > MAX_ZOOM:
                    self.zoom_target = MAX_ZOOM
                self.map_layer.center(self.map_layer.view_rect.center)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.scrolling = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.scrolling = False

            if event.type == pygame.MOUSEMOTION:
                if self.scrolling:
                    self.map_layer.view_rect.x -= event.rel[0] / self.map_layer.zoom
                    self.map_layer.view_rect.y -= event.rel[1] / self.map_layer.zoom
                    self.map_layer.center(self.map_layer.view_rect.center)

    def events(self):
        events = pygame.event.get()
        self.handle_camera_events(events)
        for obj in self.clickable_objects:
            obj.handle_events(events)

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        if abs(self.map_layer.zoom - self.zoom_target) > 0.01:
            self.map_layer.zoom += (self.zoom_target - self.map_layer.zoom) / 5
            self.map_layer.center(self.map_layer.view_rect.center)
        for obj in self.objects.sprites:
            obj.update(self.map_layer.view_rect)

    def draw(self):
        self.win.fill(BLACK)
        self.map_layer.draw(self.win, self.win.get_rect())
        self.objects.draw(self.win)
        pygame.display.update()
