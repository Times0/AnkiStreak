import os

import pygame.sprite
from constants import *
import pytmx

cwd = os.path.dirname(__file__)


class OrderedGroup(pygame.sprite.Group):
    def __init__(self, *sprites):
        super().__init__(*sprites)

    def draw(self, surface):
        sprites = self.sprites()
        surface_blit = surface.blit
        for spr in sorted(sprites, key=lambda sprite: sprite.rect.bottom):
            self.spritedict[spr] = surface_blit(spr.image, spr.rect)
        self.lostsprites = []


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, image, size, *groups):
        super().__init__()
        self.add(*groups)
        self.image = image
        self.rect = pygame.Rect(pos, (int(size[0]), int(size[1])))
        self.image = pygame.transform.scale(self.image, self.rect.size).convert_alpha()


class Clickable:
    def __init__(self):
        super().__init__()
        self.image = None
        self.rect = None

        self.clicked = False
        self.hovered = False

        self.image_hovered = None

    def render_hovered(self):
        self.image_hovered = self.image.copy()
        self.image_hovered.fill((255, 255, 255, 100), special_flags=pygame.BLEND_RGBA_MULT)

    def handle_event(self, events):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                was_hover = self.hovered
                self.hovered = self.rect.collidepoint(event.pos)
                if self.hovered and not was_hover:
                    self.on_hover()
                elif not self.hovered and was_hover:
                    self.on_unhover()

    def on_hover(self):
        self.hovered = True
        pygame.mouse.set_cursor(*pygame.cursors.diamond)

    def on_unhover(self):
        self.hovered = False
        pygame.mouse.set_cursor(*pygame.cursors.arrow)

    def draw(self, surface):
        if self.hovered:
            surface.blit(self.image_hovered, self.rect)
        else:
            surface.blit(self.image, self.rect)


class Building(Clickable):
    def __init__(self, pos, image, size):
        super().__init__()
        self.image = image
        self.rect = pygame.Rect(pos, (int(size[0]), int(size[1])))
        self.image = pygame.transform.scale(self.image, self.rect.size).convert_alpha()

        self.render_hovered()


class Game:
    def __init__(self, win):
        self.game_is_on = True
        self.win = win

        self.tmx_data = pytmx.load_pygame("../map.tmx")
        self.sprite_group = OrderedGroup()
        self.objects = OrderedGroup()
        self.clickables = []
        self.load_data()

    def load_data(self):
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, image in layer.tiles():
                    pos = (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight)
                    Tile(pos, image, (self.tmx_data.tilewidth, self.tmx_data.tileheight), self.sprite_group)
        for obj in self.tmx_data.objects:
            pos = (obj.x, obj.y)
            if obj.type in ("Tree", "Stairs", "Bridge"):
                Tile(pos, obj.image, (obj.width, obj.height), self.objects)
            elif obj.type == "Building":
                b = Building(pos, obj.image, (obj.width, obj.height))
                self.clickables.append(b)

    def run(self):
        clock = pygame.time.Clock()
        while self.game_is_on:
            clock.tick(30)
            self.events()
            self.draw(self.win)

    def events(self):
        events = pygame.event.get()
        for obj in self.clickables:
            obj.handle_event(events)
        for event in events:
            if event.type == pygame.QUIT:
                self.game_is_on = False

    def draw(self, win):
        win.fill(BLACK)
        self.sprite_group.draw(win)
        self.objects.draw(win)
        for obj in self.clickables:
            obj.draw(win)
        pygame.display.update()
