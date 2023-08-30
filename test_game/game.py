import json
import logging
import os.path
from datetime import datetime

import pygame.sprite
import pyscroll
import pytmx
from PygameUIKit import Group
from PygameUIKit.button import ButtonPngIcon
from pygame import Color

from backend.farms import Farm, PlantSpot
from backend.inventory import Inventory
from backend.objects import GameObject, SortedGroup, PointWithZoom
from backend.shop import Wallet, Shop
from backend.tuxemons import TuxemonInventory
from boring import config
from boring import imgs
from boring.config import *
from boring.utils import *
from frontend.indicators import CardIndicators, CoinsIndicator
from frontend.screens.UiInventory import InventoryUI
from frontend.screens.UiPopup import Popup
from frontend.screens.UiShop import ShopUI
from frontend.screens.UiTuxemon import TuxemonUI
from frontend.ui_manager import UIManager

cwd = os.path.dirname(__file__)
logger = logging.getLogger(__name__)


class Game:
    def __init__(self, win):
        self.time_since_last_late_update = 1000  # 1000 for late update now
        self.win = win
        self.running = True

        # _____________________Back___________________________________#
        self.inventory = Inventory()
        self.wallet = Wallet(money=1000)
        self.shop = Shop(wallet=self.wallet, inventory=self.inventory)
        self.tuxemon_inventory = TuxemonInventory(inventory=self.inventory)

        # ______________________TMX and pyscroll_____________________________________#
        self.ptmx = Pytmx(win)
        for farm in self.ptmx.farms:
            farm.link_inventory(self.inventory)

        # _____________________UI Manager___________________________________#
        self.ui_manager = UIManager()
        self.inventoryUI = InventoryUI(self.inventory, manager=self.ui_manager)
        self.shopUI = ShopUI(self.shop, manager=self.ui_manager)
        self.tuxemonUI = TuxemonUI(self.tuxemon_inventory, manager=self.ui_manager)

        self.learning_indicator = CardIndicators(manager=self.ui_manager)
        self.coin_indicator = CoinsIndicator(manager=self.ui_manager)
        self.wallet.link_ui(self.coin_indicator)

        self.ui_manager.add_elements([
            self.inventoryUI,
            self.shopUI,
            self.tuxemonUI,
            self.learning_indicator,
            self.coin_indicator
        ])

        # _____________________UI___________________________________#
        self.easy_ui = Group()
        self.btn_menu = ButtonPngIcon(imgs.btn_inventory, Color("gray"), lambda: self.ui_manager.open("inventory"))
        self.btn_shop = ButtonPngIcon(imgs.btn_shop, Color("gray"), lambda: self.ui_manager.open("shop"))
        self.btn_tuxemon = ButtonPngIcon(imgs.btn_tuxemon, Color("gray"), lambda: self.ui_manager.open("tuxemon"))
        self.easy_ui.add(self.btn_menu)
        self.easy_ui.add(self.btn_shop)
        self.easy_ui.add(self.btn_tuxemon)

        self.ui_elements = [self.easy_ui]
        self.special_ui = []

        self.anki_data_json = None
        self.load_save()
        self.load_anki_data()

    def load_anki_data(self):
        self.anki_data_json = json.load(open(anki_data_path, "r"))
        self.learning_indicator.set_nb_cards_total(self.anki_data_json["nb_cards_to_review_today"])

        self.update_learned_cards()

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            dt = clock.tick(FPS) / 1000
            self.time_since_last_late_update += dt
            print(f"\rFPS: {clock.get_fps()}", end="")
            self.events()
            self.update(dt)
            if self.time_since_last_late_update >= 1000 / LATE_UPDATE_FPS:
                self.time_since_last_late_update = 0
                self.late_update()
            self.draw(self.win)

    def events(self):
        events = pygame.event.get()

        # If no game window is open, we handle basic game events
        if not self.ui_manager.active_element:
            self.ptmx.handle_events(events)
            for e in self.ui_elements:
                e.handle_events(events)

        for gw in self.special_ui:
            if gw.isVisible():
                gw.handle_events(events)

        # important events
        for event in events:
            self.ui_manager.handle_event(event)
            if event.type == pygame.QUIT:
                self.running = False
                self.dump_save()

    def update(self, dt):
        self.ptmx.update(dt)
        self.ui_manager.update(dt)

    def late_update(self):
        """Ran every seconds"""
        pass

    def update_learned_cards(self):
        self.anki_data_json = json.load(open(anki_data_path, "r"))
        data = self.anki_data_json
        if not "time_ordinal" in data:
            return  # no assets yet
        if data["time_ordinal"] != datetime.today().toordinal():
            logger.warning(f"Weird, the ordinal date is not today's date ({data['time_ordinal']} "
                           f"!= {datetime.today().toordinal()})")
            self.learning_indicator.set_nb_cards_learned(0)
            return
        else:
            prev = self.learning_indicator.nb_cards_learned
            self.learning_indicator.set_nb_cards_learned(data["nb_cards_learned_today"])

            # If we learned cards
            if data["nb_cards_learned_today"] > prev:
                # We water all the plants based on the percentage of cards learned
                max_watering = config.MAX_WATERING
                learned_today = data["nb_cards_learned_today"]
                learned_since_last_connection = learned_today - prev
                percentage = (learned_since_last_connection / self.learning_indicator.nb_cards_total)
                nb_watering = int(percentage * max_watering) + 1
                print(f"learned {learned_today} cards today, {learned_since_last_connection} since last connection, "
                      f"percentage: {percentage}, nb_watering: {nb_watering}")
                for farm in self.ptmx.farms:
                    farm.water_all(nb_watering)

                self.create_popup(f"You learned {learned_since_last_connection} cards ! +{nb_watering} watering !")

    def create_popup(self, text):
        popup = Popup(text=text, manager=self.ui_manager)
        self.ui_manager.add_popop(popup)

    def draw(self, win):
        self.win.fill(Color("black"))
        self.ptmx.draw(win)
        self.draw_ui(win)
        pygame.display.flip()

    def draw_ui(self, win):
        W = win.get_width()
        self.btn_menu.draw(win, W - self.btn_menu.rect.width - 10, 10)
        self.btn_shop.draw(win, W - self.btn_shop.rect.width - 10 - self.btn_menu.rect.width - 10, 10)
        self.btn_tuxemon.draw(win, W - self.btn_tuxemon.rect.width - 10 -
                              self.btn_menu.rect.width - 10 - self.btn_shop.rect.width - 10, 10)
        self.ui_manager.draw(win)

    def dump_save(self):
        try:
            data = {}

            # save farm state
            try:
                for farm in self.ptmx.farms:
                    data[farm.name] = farm.dump()
            except Exception as e:
                raise RuntimeError(f"Error while dumping farm assets: {str(e)}")

            try:
                data["inventory"] = self.inventory.dump()
            except Exception as e:
                raise RuntimeError(f"Error while dumping inventory assets: {str(e)}")

            try:
                data["cards_learned_today"] = self.learning_indicator.nb_cards_learned
            except Exception as e:
                raise RuntimeError(f"Error while dumping learning indicator assets: {str(e)}")

            # save time
            try:
                data["time"] = datetime.now().toordinal()
            except Exception as e:
                raise RuntimeError(f"Error while dumping time assets: {str(e)}")

            # save wallet
            try:
                data["wallet"] = self.wallet.dump()
            except Exception as e:
                raise RuntimeError(f"Error while dumping wallet assets: {str(e)}")

            # Save assets to JSON file
            try:
                with open(os.path.join(save_folder, "game_state.json"), "w") as f:
                    json.dump(data, f, indent=4)
            except Exception as e:
                raise RuntimeError(f"Error while writing assets to file: {str(e)}")

        except Exception as e:
            print(f"An error occurred while dumping assets: {str(e)}")

        self.dump_tuxemon()

    def dump_tuxemon(self):
        data = self.tuxemon_inventory.dump()
        with open(os.path.join(config.save_folder, "tuxemon.json"), "w") as f:
            json.dump(data, f, indent=4)

    def load_save(self):
        try:
            with open(os.path.join(config.save_folder, "game_state.json"), "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            # Handle the case when the file is not found
            print("File not found. Initializing with default assets.")
            data = {}  # or any other default assets structure you want to use

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

        # load tuxemon
        self.load_tuxemon()

    def load_tuxemon(self):
        try:
            with open(os.path.join(config.save_folder, "tuxemon.json"), "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            # Handle the case when the file is not found
            print("File not found. Initializing with default assets.")
            data = {}
        print(data)
        self.tuxemon_inventory.load(data)


class Pytmx:
    def __init__(self, win):
        self.win = win
        self.data_tmx = pytmx.load_pygame(os.path.join(cwd, "assets", "map", "map_with_objects.tmx"))
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
