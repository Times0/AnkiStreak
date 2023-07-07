import math
import os
from colors import *
import pyscroll
import pygame.sprite
from config import *
import pytmx
from utils import clamp

from farms import Farm, PlantSpot
from objects import *

cwd = os.path.dirname(__file__)



class Game:
    def __init__(self, win):
        self.win = win
        self.running = True

        # ______________________TMX and pyscroll_____________________________________#
        self.data_tmx = pytmx.load_pygame(os.path.join(cwd, "data","map", "map_with_objects.tmx"))
        pyscroll_data = pyscroll.data.TiledMapData(self.data_tmx)
        self.map_layer = pyscroll.BufferedRenderer(pyscroll_data, self.win.get_size(), clamp_camera=True)
        self.farms = []
        self.interactable_objects = []
        self.special_tiles = []
        self.objects = SortedGroup()
        self.load_objects()
        self.load_special_tiles()

        # _____________________IDK___________________________________#
        self.is_scrolling = False
        self.map_layer.zoom = 1
        self.zoom_target = self.map_layer.zoom
        self.needs_update = False

        self.update(force=True)

    def load_objects(self):
        dict_future_rects = {}
        print(list(self.data_tmx.objectgroups))
        for obj_layer in self.data_tmx.objectgroups:
            if obj_layer.name == "Rects":
                for obj in obj_layer:
                    # retrieve pytmx rect object
                    points = [PointWithZoom((p.x, p.y)) for p in obj.points]
                    dict_future_rects[obj.name] = points

            if obj_layer.name == "Objects":
                for obj in obj_layer:
                    if obj.type == "Farm":
                        associated_rect = dict_future_rects[obj.name]
                        o = Farm((obj.x, obj.y), (obj.width, obj.height), obj.image, associated_rect)
                        self.interactable_objects.append(o)
                        self.objects.add(o)
                        if obj.name == "Farm1":
                            self.farms.insert(0, o)
                        elif obj.name == "Farm2":
                            self.farms.append(o)
                    else:
                        self.objects.add(GameObject((obj.x, obj.y), (obj.width, obj.height), obj.image))

    def load_special_tiles(self):
        for layer in self.data_tmx.layers:
            if layer.name == "Plantations1":
                for x, y, gid in layer:
                    if gid != 0:
                        plant = PlantSpot((x * self.data_tmx.tilewidth, y * self.data_tmx.tileheight))
                        self.farms[0].add_plant_location(plant)
            elif layer.name == "Plantations2":
                for x, y, gid in layer:
                    if gid != 0:
                        plant = PlantSpot((x * self.data_tmx.tilewidth, y * self.data_tmx.tileheight))
                        self.farms[1].add_plant_location(plant)

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            clock.tick(FPS)
            self.needs_update = False  # Modified if scrolling the map or zooming
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
                self.zoom_target = clamp(self.zoom_target, MIN_ZOOM, MAX_ZOOM)
                self.map_layer.center(self.map_layer.view_rect.center)
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.needs_update = True
                if event.button == 2:
                    self.is_scrolling = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:
                    self.is_scrolling = False

            if event.type == pygame.MOUSEMOTION:
                self.needs_update = True
                if self.is_scrolling:
                    self.map_layer.view_rect.x -= event.rel[0] / self.map_layer.zoom
                    self.map_layer.view_rect.y -= event.rel[1] / self.map_layer.zoom
                    self.map_layer.center(self.map_layer.view_rect.center)

    def events(self):
        events = pygame.event.get()
        self.handle_camera_events(events)
        for obj in self.interactable_objects:
            obj.handle_events(events)

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

    def update(self, force=False):
        if abs(self.map_layer.zoom - self.zoom_target) > 10 ** (-3):
            self.map_layer.zoom += (self.zoom_target - self.map_layer.zoom) / 2
            self.map_layer.center(self.map_layer.view_rect.center)
            self.needs_update = True
        if self.needs_update or force:
            for obj in self.objects.sprites + self.interactable_objects:
                obj.update(self.map_layer.view_rect)

    def draw(self):
        self.win.fill(BLACK)
        self.map_layer.draw(self.win, self.win.get_rect())
        self.objects.draw(self.win)
        for obj in self.special_tiles:
            obj.draw(self.win)
        pygame.display.update()
