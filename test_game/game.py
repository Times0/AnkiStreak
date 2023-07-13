import json
import math
import os
from datetime import datetime

import colors
from colors import *
import pyscroll
import pygame.sprite
from config import *
import pytmx
from utils import clamp
from ui import *
from farms import Farm, PlantSpot, Inventory
from objects import *

from PygameUIKit import button, Group

cwd = os.path.dirname(__file__)


class Game:
    def __init__(self, win):
        self.time_since_last_late_update = 1000  # for late update now
        self.win = win
        self.running = True

        self.inventory = Inventory()
        # ______________________TMX and pyscroll_____________________________________#
        self.data_tmx = pytmx.load_pygame(os.path.join(cwd, "data", "map", "map_with_objects.tmx"))
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
        self.map_layer.zoom = START_ZOOM
        self.zoom_target = self.map_layer.zoom
        self.needs_update = False
        self.update_camera(force=True)
        # _____________________UI___________________________________#
        self.ui = Group()
        self.btn_menu = button.ButtonPngIcon(imgs.btn_menu, colors.GRAY, self.toggle_menu)
        self.ui.add(self.btn_menu)

        self.learning_indicator = CardIndicators()
        self.menu = InventoryUI(self.inventory)

        self.load_save()

    def load_objects(self):
        dict_future_rects = {}
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
                        o = Farm((obj.x, obj.y),
                                 (obj.width, obj.height),
                                 obj.image,
                                 associated_rect,
                                 self.inventory,
                                 name=obj.name)
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
            dt = clock.tick(FPS)
            self.time_since_last_late_update += dt
            # print(f"FPS: {clock.get_fps()}")
            self.needs_update = False  # Modified if scrolling the map or zooming
            self.events()
            self.update(dt)
            self.update_camera()
            if self.time_since_last_late_update >= 1000 / LATE_UPDATE_FPS:
                self.time_since_last_late_update = 0
                self.late_update()
            self.draw(self.win)

    def handle_camera_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEWHEEL and ALLOW_SCROLLING:
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
        self.ui.handle_events(events)
        if self.menu.is_open:
            pass
        else:
            self.handle_camera_events(events)
            for obj in self.interactable_objects:
                obj.handle_events(events)

        # important events
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                self.dump_save(save_path)

    def late_update(self):
        """Ran every seconds"""
        prev = self.learning_indicator.counter
        with open(cards_learned_path, "r") as f:
            # Check if first line is today's ordinal
            lines = f.readlines()

            first_line = lines[0]
            today = datetime.today().toordinal()
            if int(first_line) != today:
                self.learning_indicator.set(0)
                return
            second_line = lines[1]
            nb = int(second_line)
            if nb > prev:
                self.learning_indicator.counter = nb
                self.learning_indicator.render()
                for i in range(nb - prev):
                    for farm in self.farms:
                        farm.water_all()
            elif nb < prev:
                print("Must be new day")
                self.learning_indicator.counter = nb
                self.learning_indicator.render()

    def update(self, dt):
        for obj in self.objects.sprites + self.interactable_objects+ self.farms:
            obj.update(dt)

    def update_camera(self, force=False):
        if abs(self.map_layer.zoom - self.zoom_target) > 10 ** (-3):
            self.map_layer.zoom += (self.zoom_target - self.map_layer.zoom) / 2
            self.map_layer.center(self.map_layer.view_rect.center)
            self.needs_update = True
        if self.needs_update or force:
            for obj in self.objects.sprites + self.interactable_objects:
                obj.update_camera(self.map_layer.view_rect)
        else:
            for farm in self.farms:
                farm.update_camera(self.map_layer.view_rect)

    def draw(self, win):
        self.win.fill(BLACK)
        self.map_layer.draw(win, win.get_rect())
        self.objects.draw(win)
        for obj in self.special_tiles:
            obj.draw(win)
        self.draw_ui(win)
        pygame.display.update()

    def draw_ui(self, win):
        W = win.get_width()
        self.btn_menu.draw(win, W - self.btn_menu.rect.width - 10, 10)
        self.learning_indicator.draw(win)

        if self.menu.is_open:
            self.menu.draw(win)

    def dump_save(self, path):
        # Check if save_path is a valid path
        if not os.path.isdir(os.path.dirname(path)):
            raise ValueError(f"Invalid path: {os.path.dirname(path)} does not exist.")

        try:
            data = {}

            # save farm state
            try:
                for farm in self.farms:
                    data[farm.name] = farm.dump()
            except Exception as e:
                raise RuntimeError(f"Error while dumping farm data: {str(e)}")

            # save inventory state
            try:
                data["inventory"] = self.inventory.dump()
            except Exception as e:
                raise RuntimeError(f"Error while dumping inventory data: {str(e)}")

            # save learning indicator state
            try:
                data["cards_learned_today"] = self.learning_indicator.counter
            except Exception as e:
                raise RuntimeError(f"Error while dumping learning indicator data: {str(e)}")

            # save time
            try:
                data["time"] = datetime.now().toordinal()
            except Exception as e:
                raise RuntimeError(f"Error while dumping time data: {str(e)}")

            # Save data to JSON file
            try:
                with open(path, "w") as f:
                    json.dump(data, f, indent=4)
            except Exception as e:
                raise RuntimeError(f"Error while writing data to file: {str(e)}")

            print(f"Data dumped to {path} !")


        except Exception as e:
            print(f"An error occurred while dumping data: {str(e)}")

    def load_save(self):
        try:
            with open(save_path, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            # Handle the case when the file is not found
            print("File not found. Initializing with default data.")
            data = {}  # or any other default data structure you want to use

        # load farm state
        for farm in self.farms:
            if farm.name in data.keys():
                farm.load(data[farm.name])

        # load inventory state
        if "inventory" in data.keys():
            self.inventory.load(data["inventory"])

        # load learning indicator state
        if "cards_learned_today" in data.keys():
            if data["time"] != datetime.now().toordinal():
                self.learning_indicator.set(0)
            else:
                self.learning_indicator.set(data["cards_learned_today"])

    def toggle_menu(self):
        self.menu.is_open = not self.menu.is_open
