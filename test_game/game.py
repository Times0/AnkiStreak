import json
import logging
import os.path
import pygame.sprite
import pyscroll
import pytmx
from PygameUIKit import Group
from PygameUIKit.button import ButtonPngIcon, ButtonText
from pygame import Color, Vector2

from PygameUIKit.slider import Slider
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
from frontend.screens.UiTuxemon import TuxemonUI
from frontend.ui_manager import UIManager
from test_game.boring.imgs import load_font
from test_game.frontend.npc import NPC
from test_game.frontend.screens.UiShop import ShopUI
import datetime

if not DEBUG:
    import aqt.utils
    from aqt import gui_hooks, mw

cwd = os.path.dirname(__file__)
logger = logging.getLogger(__name__)

today_ord = datetime.date.today().toordinal() + 1  #

cool_numbers = {
    1: "1st",
    2: "2nd",
    3: "3rd"
}


def enhance_numbers(n):
    if n in cool_numbers:
        return cool_numbers[n]
    else:
        return f"{n}th"


def get_new_streak() -> tuple[int, int]:
    if not mw.col.conf.get("streak"):
        return 1, today_ord

    today_ordinal = today_ord
    streak, last_day_ordinal = mw.col.conf["streak"]

    if today_ordinal == last_day_ordinal:
        pass
    elif today_ordinal == last_day_ordinal + 1:
        streak += 1
    else:
        streak = 1
    return streak, today_ordinal


def change_music_volume(value):
    pygame.mixer.music.set_volume(value / 100)


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
        btn_font = load_font("title.otf", 40)
        self.easy_ui = Group()
        self.btn_menu = ButtonPngIcon(imgs.btn_inventory, lambda: self.ui_manager.open("inventory"), Color("gray"))
        self.btn_shop = ButtonPngIcon(imgs.btn_shop, lambda: self.ui_manager.open("shop"), Color("gray"))
        self.btn_tuxemon = ButtonPngIcon(imgs.btn_tuxemon, lambda: self.ui_manager.open("tuxemon"), Color("gray"))
        self.button_start_learning = ButtonText("Start learning", font=btn_font, rect_color=Color(124, 197, 96),
                                                font_color=Color("white"), border_radius=10)
        self.button_start_learning.connect(self.start_learning)
        self.slider_music = Slider(0, 100, 1, ui_group=self.easy_ui)

        self.easy_ui.add(self.button_start_learning)
        self.easy_ui.add(self.btn_menu)
        self.easy_ui.add(self.btn_shop)
        self.easy_ui.add(self.btn_tuxemon)

        self.ui_elements = [self.easy_ui]
        self.special_ui = []

        self.anki_data_json = None
        self.load_save()
        self.load_anki_data()

        # Music
        pygame.mixer.music.load(os.path.join(cwd, "assets", "music", "music.mp3"))
        pygame.mixer.music.play(-1)
        self.slider_music.current_value = 100
        self.slider_music.connect(lambda: change_music_volume(self.slider_music.get_value()))

    def start_learning(self):
        self.running = False

    def load_anki_data(self):
        # if not os.path.exists(anki_data_path):
        #     self.anki_data_json = {"time_ordinal": datetime.today().toordinal(),
        #                            "nb_cards_to_review_today": 0,
        #                            "nb_cards_learned_today": 0}
        #     json.dump(self.anki_data_json, open(anki_data_path, "w"))
        self.anki_data_json = json.load(open(anki_data_path, "r"))
        self.learning_indicator.set_nb_cards_total(self.anki_data_json["nb_cards_to_review_today"])

        self.update_learned_cards()
        if not config.DEBUG:
            self.check_for_streak_earnings()

    def check_for_streak_earnings(self):
        previous_streak, _ = mw.col.conf.get("streak", (-float('inf'), 0))
        streak, ordinal = get_new_streak()
        mw.col.conf["streak"] = streak, ordinal

        if streak > previous_streak:
            # Give the player some money depending on the streak
            money = 100 * streak
            self.wallet.add_money(money)
            self.create_popup("Good Job !",
                              f"You have a {streak} day(s) streak !\n Here is a little reward !\n +{money} coins !")

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            dt = clock.tick(FPS) / 1000
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

        # If no game window is open, we handle basic game events
        if not self.ui_manager.active_element:
            self.ptmx.handle_events(events)
            for e in self.ui_elements:
                for event in events:
                    e.handle_event(event)

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
        if "time_ordinal" not in data:
            return
        if data["time_ordinal"] != datetime.datetime.today().toordinal():
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
                print(f"learned {learned_today} cards today")
                learned_since_last_connection = learned_today - prev
                percentage = (learned_since_last_connection / self.learning_indicator.nb_cards_total)
                nb_watering = int(percentage * max_watering) + 1
                print(f"learned {learned_today} cards today, {learned_since_last_connection} since last connection, "
                      f"percentage: {percentage}, nb_watering: {nb_watering}")
                for farm in self.ptmx.farms:
                    farm.water_all(nb_watering)

                self.create_popup("Good Job !",
                                  f"You learned {learned_since_last_connection} since last time !\n"
                                  f"Your plants have been watered accordingly !")

    def create_popup(self, title, text):
        popup = Popup(title=title, text=text, manager=self.ui_manager)
        self.ui_manager.add_popop(popup)

    def draw(self, win):
        self.win.fill(Color("black"))
        self.ptmx.draw(win)
        self.draw_ui(win)
        pygame.display.flip()

    def draw_ui(self, win):
        W = win.get_width()
        H = win.get_height()
        self.btn_menu.draw(win, W - self.btn_menu.rect.width - 10, 10)
        self.btn_shop.draw(win, W - self.btn_shop.rect.width - 10 - self.btn_menu.rect.width - 10, 10)
        x = W - self.btn_tuxemon.rect.width - 10 - self.btn_menu.rect.width - 10 - self.btn_shop.rect.width - 10
        self.btn_tuxemon.draw(win, x, 10)
        self.button_start_learning.draw(win, W - self.button_start_learning.rect.width - 10,
                                        H // 2 - self.button_start_learning.rect.height // 2)
        self.slider_music.draw(win, 10, H - self.slider_music.rect.height - 10, 200, 10)
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
                data["time"] = datetime.datetime.now().toordinal()
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
        with open(os.path.join(config.save_folder, "tuxemon.json"), "w+") as f:
            json.dump(data, f)

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
            if data["time"] != datetime.datetime.now().toordinal():
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
                self.tuxemon_inventory.load(data)

        except FileNotFoundError:
            print("File not found. Initializing with default assets.")
            self.tuxemon_inventory.add_default_tuxemons()


class Pytmx:
    def __init__(self, win):
        self.win = win
        self.data_tmx = pytmx.load_pygame(os.path.join(cwd, "assets", "map", "map_with_objects.tmx"))
        pyscroll_data = pyscroll.data.TiledMapData(self.data_tmx)
        self.map_layer = pyscroll.BufferedRenderer(pyscroll_data, self.win.get_size(), clamp_camera=True)
        self.farms = []
        self.interactable_objects = []
        self.objects = SortedGroup()
        self.objects_under_npc = SortedGroup()

        self.PATH_POINTS = []
        self.load_objects()
        self.load_special_tiles()

        # Game attributes
        self.map_layer.zoom = START_ZOOM
        self.zoom_target = self.map_layer.zoom
        self.is_scrolling = False
        self.requires_update = False

        # ______________________NPCs_____________________________________#
        self.npcs: list[NPC] = []
        for name in ['healer_f', 'healer_m', 'mage_f', 'mage_m', 'ninja_f', 'ninja_m', 'ranger_f', 'ranger_m',
                     'townfolk1_f', 'townfolk1_m', 'warrior_f', 'warrior_m']:
            self.npcs.append(NPC(name, self.PATH_POINTS))

        for npc in self.npcs:
            self.objects.add(npc)

        self.update_camera(force=True)

    def load_special_tiles(self):
        for layer in self.data_tmx.layers:
            if layer.name == "Plantations1":
                for x, y, gid in layer:
                    if gid != 0:
                        vec = Vector2(x * self.data_tmx.tilewidth, y * self.data_tmx.tileheight)
                        plant = PlantSpot(vec)
                        self.farms[0].add_plant_location(plant)
            elif layer.name == "Plantations2":
                for x, y, gid in layer:
                    if gid != 0:
                        vec = Vector2(x * self.data_tmx.tilewidth, y * self.data_tmx.tileheight)
                        plant = PlantSpot(vec)
                        self.farms[1].add_plant_location(plant)

    def load_objects(self):
        dict_future_rects = {}
        for obj_layer in self.data_tmx.objectgroups:
            if obj_layer.name == "Rects":
                for obj in obj_layer:
                    points = [PointWithZoom((p.x, p.y)) for p in obj.points]
                    dict_future_rects[obj.name] = points

            elif obj_layer.name == "PathPoints":
                pts = []
                for obj in obj_layer:
                    pts.append((obj.x, obj.y))
                self.PATH_POINTS = pts

            elif obj_layer.name == "Objects":
                for obj in obj_layer:
                    if obj.type == "Farm":
                        associated_rect = dict_future_rects[obj.name]
                        farm = Farm(Vector2(obj.x, obj.y),
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
                        self.objects.add(GameObject(Vector2(obj.x, obj.y), (obj.width, obj.height), obj.image))

            elif obj_layer.name == "UnderNpcObjects":
                for obj in obj_layer:
                    self.objects_under_npc.add(GameObject(Vector2(obj.x, obj.y), (obj.width, obj.height),
                                                          obj.image))

    def handle_events(self, events):
        self.handle_camera_events(events)
        for obj in self.interactable_objects:
            obj.handle_events(events)

    def handle_camera_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEWHEEL and ALLOW_SCROLLING:
                if event.y > 0:
                    self.zoom_target *= 1.05
                elif event.y < 0:
                    self.zoom_target /= 1.05
                self.zoom_target = clamp(self.zoom_target, MIN_ZOOM, MAX_ZOOM)
                self.map_layer.zoom = self.zoom_target
                self.requires_update = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.requires_update = True
                if event.button == 2 or event.button == 3:
                    self.is_scrolling = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2 or event.button == 3:
                    self.is_scrolling = False

            if event.type == pygame.MOUSEMOTION:
                if self.is_scrolling:
                    self.requires_update = True
                    self.map_layer.view_rect.x -= event.rel[0] / self.map_layer.zoom
                    self.map_layer.view_rect.y -= event.rel[1] / self.map_layer.zoom

            if self.requires_update:
                self.map_layer.center(self.map_layer.view_rect.center)

    def update(self, dt):
        for obj in self.objects.sprites + self.interactable_objects + self.farms + self.objects_under_npc.sprites + self.npcs:
            obj.update(dt)
        self.update_camera()

    def update_camera(self, force=False):
        # Objects that do not need an update if the camera has not moved
        if self.requires_update or force:
            for obj in self.objects.sprites + self.interactable_objects + self.farms + self.objects_under_npc.sprites:
                obj.update_camera(self.map_layer.view_rect)
            self.requires_update = False
        # Objects that need an update even if the camera has not moved
        for npc in self.npcs + self.farms:
            npc.update_camera(self.map_layer.view_rect)

    def draw(self, win):
        self.map_layer.draw(win, win.get_rect())
        self.objects_under_npc.draw(win)
        self.objects.draw(win)
