import os
import random

import pygame.sprite
from constants import *
import pytmx
from camera import Camera

cwd = os.path.dirname(__file__)


class OrderedGroup(pygame.sprite.Group):
    def __init__(self, *sprites):
        super().__init__(*sprites)

    def draw(self, surface, camera):
        self.sprites()
        for sprite in self.sprites():
            self.spritedict[sprite] = surface.blit(sprite.image, camera.apply(sprite.rect))


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, images, size, *groups):
        super().__init__()
        self.add(*groups)
        self.images = images
        self.rect = pygame.Rect(pos, (int(size[0]), int(size[1])))
        self.images = [pygame.transform.scale(img, self.rect.size).convert_alpha() for img in self.images]
        self.image = self.images[0]
        self.frame_index = 0

    def change_size(self, size):
        self.rect.size = size
        self.images = [pygame.transform.scale(img, self.rect.size).convert_alpha() for img in self.images]
        self.image = self.images[0]

    def update(self, dt):
        self.frame_index += 0.2
        if self.frame_index >= len(self.images):
            self.frame_index = 0
        self.image = self.images[int(self.frame_index)]


class Clickable(pygame.sprite.Sprite):
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
        self.all_sprites = OrderedGroup()
        self.clickables = []
        self.load_data()

        self.camera = Camera(2, (0, 0))  # zoom level, position
        self.update_sprites_size()
        self.holding = False

    def load_data(self):
        for layer in self.tmx_data.visible_layers:
            if not isinstance(layer, pytmx.TiledTileLayer):
                continue
            for x, y, image in layer.tiles():
                images = []
                for gid, props in self.tmx_data.tile_properties.items():
                    if image == self.tmx_data.get_tile_image_by_gid(gid):
                        if props.get("frames"):
                            images = []
                            for frame in props["frames"]:
                                images.append(self.tmx_data.get_tile_image_by_gid(frame.gid))

                if not images:
                    images = [image]

                pos = (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight)
                Tile(pos, images, (self.tmx_data.tilewidth, self.tmx_data.tileheight), self.all_sprites)
        for obj in self.tmx_data.objects:
            pos = (obj.x, obj.y)
            if obj.type in ("Tree", "Stairs", "Bridge"):
                Tile(pos, [obj.image], (obj.width, obj.height), self.all_sprites)
            elif obj.type == "Building":
                b = Building(pos, obj.image, (obj.width, obj.height))
                # self.clickables.append(b)
                self.all_sprites.add(b)

    def update_sprites_size(self):
        for i in range(len(self.all_sprites.sprites())):
            if isinstance(self.all_sprites.sprites()[i], Tile):
                previous_size = self.all_sprites.sprites()[i].rect.size
                self.all_sprites.sprites()[i].change_size((int(previous_size[0] * self.camera.zoom_level+1),
                                                           int(previous_size[1] * self.camera.zoom_level+1)))

            else:
                previous_size = self.all_sprites.sprites()[i].rect.size
                self.all_sprites.sprites()[i].image = \
                    pygame.transform.scale(self.all_sprites.sprites()[i].image,
                                           (int(previous_size[0] * self.camera.zoom_level),
                                            int(previous_size[1] * self.camera.zoom_level)))

    def run(self):
        clock = pygame.time.Clock()
        while self.game_is_on:
            dt = clock.tick(30)
            # print(f"\r{clock.get_fps()}", end="")
            self.events()
            self.update(dt)
            self.draw(self.win)

    def events(self):
        events = pygame.event.get()
        for obj in self.clickables:
            obj.handle_event(events)
        for event in events:
            if event.type == pygame.QUIT:
                self.game_is_on = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:  # middle mouse button
                self.holding = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 2:
                self.holding = False
            if event.type == pygame.MOUSEMOTION and self.holding:
                self.camera.move(event.rel)

    def update(self, dt):
        self.all_sprites.update(dt)

    def draw(self, win):
        win.fill(BLACK)
        self.all_sprites.draw(win, self.camera)
        pygame.display.flip()
