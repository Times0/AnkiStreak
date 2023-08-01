import json
from datetime import datetime

import pygame.sprite
import pyscroll
import pytmx
from PygameUIKit import Group

from boring import config
from boring.config import *
from boring.utils import *
from objects import *
from test_game.game_objects.farms import Farm
from test_game.game_objects.farms import PlantSpot
from test_game.game_objects.shop import Wallet
from ui import *

cwd = os.path.dirname(__file__)


class Game:
    def __init__(self, win):
        self.time_since_last_late_update = 1000  # 1000 for late update now
        self.win = win
        self.running = True

        # _____________________Back___________________________________#
        self.inventory = Inventory()
        self.wallet = Wallet(money=1000)
        self.shop = Shop(wallet=self.wallet, inventory=self.inventory)

        # ______________________TMX and pyscroll_____________________________________#
        self.ptmx = Pytmx(win)
        for farm in self.ptmx.farms:
            farm.link_inventory(self.inventory)

        # _____________________UI___________________________________#
        self.inventoryUI = InventoryUI(self.inventory)
        self.shopUI = ShopUI(self.shop)
        self.learning_indicator = CardIndicators()
        self.coin_indicator = CoinsIndicator()
        self.wallet.link_ui(self.coin_indicator)
        self.easy_ui = Group()
        self.btn_menu = button.ButtonPngIcon(imgs.btn_inventory, colors.GRAY, self.inventoryUI.toggle_visibility)
        self.btn_shop = button.ButtonPngIcon(imgs.btn_shop, colors.GRAY, self.shopUI.toggle_visibility)
        self.easy_ui.add(self.btn_menu)
        self.easy_ui.add(self.btn_shop)
        self.ui_elements = [self.learning_indicator, self.coin_indicator, self.easy_ui]
        self.game_windows = [self.inventoryUI, self.shopUI]
        self.load_save()

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            dt = clock.tick(FPS)
            self.time_since_last_late_update += dt
            # print(f"\rFPS: {clock.get_fps()}", end="")
            self.events()
            self.update(dt)
            if self.time_since_last_late_update >= 1000 / LATE_UPDATE_FPS:
                self.time_since_last_late_update = 0
                self.late_update()
            self.draw(self.win)

    def events(self):
        events = pygame.event.get()

        if not any([e.isVisible() for e in self.game_windows]):
            self.ptmx.handle_events(events)
            for e in self.ui_elements:
                e.handle_events(events)

        for gw in self.game_windows:
            if gw.isVisible():
                gw.handle_events(events)

        # important events
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                self.dump_save(save_path)

    def update(self, dt):
        self.ptmx.update(dt)

    def late_update(self):
        """Ran every seconds"""
        self.update_learned_cards()

    def update_learned_cards(self):
        prev = self.learning_indicator.nb_cards_learned
        with open(cards_learned_path, "r") as f:
            # Check if first line is today's ordinal
            lines = f.readlines()
            first_line = lines[0]
            today = datetime.today().toordinal()
            if int(first_line) != today:
                print("Weird, first line is not today's ordinal")
                self.learning_indicator.set_nb_cards_learned(0)
                return
            second_line = lines[1]
            nb = int(second_line)
            if nb > prev:
                self.learning_indicator.set_nb_cards_learned(nb)
                for i in range(nb - prev):
                    for farm in self.ptmx.farms:
                        farm.water_all()
            elif nb < prev:
                print("Must be new day")
                self.learning_indicator.set_nb_cards_learned(0)

    def draw(self, win):
        self.win.fill(BLACK)
        self.ptmx.draw(win)
        self.draw_ui(win)
        pygame.display.update()

    def draw_ui(self, win):
        W = win.get_width()
        self.btn_menu.draw(win, W - self.btn_menu.rect.width - 10, 10)
        self.btn_shop.draw(win, W - self.btn_shop.rect.width - 10 - self.btn_menu.rect.width - 10, 10)

        self.learning_indicator.draw(win, 30, 15, 200, 30)
        self.coin_indicator.draw(win, 5, self.learning_indicator.rect.h + 200, 200, 30)

        if self.inventoryUI.isVisible():
            w, h = 400, 700
            x = (win.get_width() - w) // 2
            y = (win.get_height() - h) // 2
            self.inventoryUI.draw(win, x, y, w, h)
        if self.shopUI.isVisible():
            w, h = 1000, 300
            x = (win.get_width() - w) // 2
            y = (win.get_height() - h) // 2

            self.shopUI.draw(win, x, y, w, h)

    def dump_save(self, path):
        # Check if save_path is a valid path
        if not os.path.isdir(os.path.dirname(path)):
            raise ValueError(f"Invalid path: {os.path.dirname(path)} does not exist.")

        try:
            data = {}

            # save farm state
            try:
                for farm in self.ptmx.farms:
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
                data["cards_learned_today"] = self.learning_indicator.nb_cards_learned
            except Exception as e:
                raise RuntimeError(f"Error while dumping learning indicator data: {str(e)}")

            # save time
            try:
                data["time"] = datetime.now().toordinal()
            except Exception as e:
                raise RuntimeError(f"Error while dumping time data: {str(e)}")

            # save wallet
            try:
                data["wallet"] = self.wallet.dump()
            except Exception as e:
                raise RuntimeError(f"Error while dumping wallet data: {str(e)}")

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
            with open(config.save_path, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            # Handle the case when the file is not found
            print("File not found. Initializing with default data.")
            data = {}  # or any other default data structure you want to use

        # load farm state
        for farm in self.ptmx.farms:
            if farm.name in data.keys():
                farm.load(data[farm.name])

        # load inventory state
        if "inventory" in data.keys():
            self.inventory.load(data["inventory"])

        # load learning indicator state
        if "cards_learned_today" in data.keys():
            if data["time"] != datetime.now().toordinal():
                self.learning_indicator.set_nb_cards_learned(0)
            else:
                self.learning_indicator.set_nb_cards_learned(data["cards_learned_today"])

        # load wallet
        if "wallet" in data.keys():
            self.wallet.load(data["wallet"])


class Pytmx:
    def __init__(self, win):
        self.win = win
        self.data_tmx = pytmx.load_pygame(os.path.join(cwd, "data", "map", "map_with_objects.tmx"))
        pyscroll_data = pyscroll.data.TiledMapData(self.data_tmx)
        self.map_layer = pyscroll.BufferedRenderer(pyscroll_data, self.win.get_size(), clamp_camera=True)
        self.farms = []
        self.interactable_objects = []
        self.special_tiles = []
        self.objects = SortedGroup()
        self.load_objects()
        self.load_special_tiles()

        # Game attributes
        self.map_layer.zoom = START_ZOOM
        self.zoom_target = self.map_layer.zoom
        self.is_scrolling = False
        self.requires_update = False

        self.update_camera(force=True)

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
                        farm = Farm((obj.x, obj.y),
                                    (obj.width, obj.height),
                                    obj.image,
                                    associated_rect,
                                    name=obj.name)
                        self.interactable_objects.append(farm)
                        self.objects.add(farm)
                        if obj.name == "Farm1":
                            self.farms.insert(0, farm)
                        elif obj.name == "Farm2":
                            self.farms.append(farm)
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

    def handle_events(self, events):
        self.handle_camera_events(events)
        for obj in self.interactable_objects:
            obj.handle_events(events)

    def handle_camera_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEWHEEL and ALLOW_SCROLLING:
                if event.y > 0:
                    self.zoom_target += 0.05
                elif event.y < 0:
                    self.zoom_target -= 0.05
                self.zoom_target = clamp(self.zoom_target, MIN_ZOOM, MAX_ZOOM)
                # self.map_layer.center(self.map_layer.view_rect.center)

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.requires_update = True
                if event.button == 2:
                    self.is_scrolling = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:
                    self.is_scrolling = False

            if event.type == pygame.MOUSEMOTION:
                self.requires_update = True
                if self.is_scrolling:
                    self.map_layer.view_rect.x -= event.rel[0] / self.map_layer.zoom
                    self.map_layer.view_rect.y -= event.rel[1] / self.map_layer.zoom
                    self.map_layer.center(self.map_layer.view_rect.center)

    def update(self, dt):
        for obj in self.objects.sprites + self.interactable_objects + self.farms:
            obj.update(dt)

        self.update_camera()

    def update_camera(self, force=False):
        if abs(self.map_layer.zoom - self.zoom_target) > 10 ** (-3):
            self.map_layer.zoom += (self.zoom_target - self.map_layer.zoom) / 2
            self.map_layer.center(self.map_layer.view_rect.center)
            self.requires_update = True
        if self.requires_update or force:
            for obj in self.objects.sprites + self.interactable_objects:
                obj.update_camera(self.map_layer.view_rect)
        else:
            for farm in self.farms:
                farm.update_camera(self.map_layer.view_rect)

    def draw(self, win):
        self.map_layer.draw(win, win.get_rect())
        self.objects.draw(win)
        for obj in self.special_tiles:
            obj.draw(win)
