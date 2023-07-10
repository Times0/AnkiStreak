import pygame

import colors
from objects import GameObject_no_img, GameObject, GameObject_no_pos, Clickable, PointWithZoom
from config import *
from colors import *
import imgs
from utils import is_point_inside_polygon, draw_menu_rect


class Item(GameObject_no_pos):
    def __init__(self, name, img):
        super().__init__((50, 50), img)
        self.name = name

    def draw(self, win):
        win.blit(self.zoom_buffer, self.rect)


class Inventory:
    def __init__(self):
        self.items = {}  # name: quantity
        self.items_data = {}  # name: Item

    def add_item(self, item: Item):
        if item.name in self.items:
            self.items[item.name] += 1
        else:
            self.items[item.name] = 1
            self.items_data[item.name] = item

    def remove_item(self, item):
        if item.name in self.items:
            self.items[item.name] -= 1
            if self.items[item.name] == 0:
                del self.items[item.name]
        else:
            raise Exception("Item not found in inventory")

    def dump(self) -> dict:
        return self.items

    def load(self, items: dict):
        self.items = items
        for item_name in items:
            self.items_data[item_name] = Item(item_name, imgs.items[item_name])

    def __getitem__(self, item_name):
        return self.items[item_name]

    def __setitem__(self, item_name, value):
        self.items[item_name] = value

    def __contains__(self, item_name):
        return item_name in self.items

    def __iter__(self):
        return iter(self.items)

    def get_item_image(self, item_name) -> pygame.Surface:
        return self.items_data[item_name].img


class FarmMenuItem(Item):
    seed = 0
    recolter = 1
    water = 2

    def __init__(self, name, img, type):
        super().__init__(name, img)
        self.type = type


class Menu(GameObject_no_img):
    def __init__(self, linked_bat, size, items):
        x_menu = linked_bat.rect.x + (linked_bat.rect.width - size[0]) // 2
        y_menu = linked_bat.rect.y - size[1] - 10
        pos = (x_menu, y_menu)
        super().__init__(pos, size)
        self.items = items
        self.is_open = False

        self.hovered_item_index = -1

        self.item_size = -1  # will be calculated in update_items_rect
        self.item_padding = 10

        self.items_rects: list[pygame.Rect] = []
        self.selected_item = None

        self.update_items_rect()

    def update_items_rect(self):
        self.items_rects = []
        self.item_size = (self.rect.width - (len(self.items) + 1) * self.item_padding) // len(self.items)
        y = self.rect.y + (self.rect.height - self.item_size) // 2

        for i, item in enumerate(self.items):
            self.items_rects.append(
                pygame.Rect((self.rect.x + self.item_padding + i * (self.item_size + self.item_padding), y),
                            (self.item_size, self.item_size)))

    def add_item(self, item):
        self.items.append(item)

    def update(self, camera_rect):
        GameObject_no_img.update(self, camera_rect)
        for i, item in enumerate(self.items):
            item.update(camera_rect)
        self.update_items_rect()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                for i, item in enumerate(self.items):
                    if self.items_rects[i].collidepoint(event.pos):
                        self.hovered_item_index = i
                        break
                    else:
                        self.hovered_item_index = -1
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.is_open = not self.is_open
                else:
                    self.is_open = False
                # Check if an item is clicked
                for i, item in enumerate(self.items):
                    if self.items_rects[i].collidepoint(event.pos):
                        self.selected_item = item
                        return

    def draw(self, win):
        # draw menu background slightly transparent black with white border
        draw_menu_rect(win, self.rect, colors.MENU_BACKGROUND)
        for i, item in enumerate(self.items):
            if self.hovered_item_index == i:
                pygame.draw.rect(win, colors.MENU_SELECTED, self.items_rects[i].inflate(10, 10), border_radius=10)

            win.blit(item.zoom_buffer, self.items_rects[i])


seeds = FarmMenuItem("seeds", imgs.seeds, FarmMenuItem.seed)
water_seeds = FarmMenuItem("water Seeds", imgs.water_seeds, FarmMenuItem.seed)
fire_seeds = FarmMenuItem("fire Seeds", imgs.fire_seeds, FarmMenuItem.seed)
bucket = FarmMenuItem("bucket", imgs.bucket, FarmMenuItem.water)
faux = FarmMenuItem("faux", imgs.faux, FarmMenuItem.recolter)
menu_items = [seeds, water_seeds, fire_seeds, bucket, faux]


class Farm(GameObject, Clickable):
    def __init__(self, pos, size, img, farm_zone, farm_inventory: Inventory, name="Farm"):
        GameObject.__init__(self, pos, size, img)
        Clickable.__init__(self, pos, size)
        self.menu = Menu(self, (66 * len(menu_items), 75), menu_items)
        self.plants_location: dict[int, PlantSpot] = {}
        self.farm_zone: list[PointWithZoom] = farm_zone
        self.name = name
        self.farm_inventory: Inventory = farm_inventory

    def add_plant_location(self, plant):
        self.plants_location[plant.id] = plant

    def get_plant_spot_id_at(self, pos):
        for plant_loc in self.plants_location.values():
            if plant_loc.rect.collidepoint(pos):
                return plant_loc.id
        return None

    def add_plant_at_pos(self, pos, plant) -> None:
        plant_id = self.get_plant_spot_id_at(pos)
        self.add_plant_at_id(plant_id, plant)

    def add_plant_at_id(self, id, plant):
        self.plants_location[id].add_plant(plant)

    def remove_plant_at_id(self, id):
        self.plants_location[id].remove_plant()

    def handle_events(self, events):
        selected_tool = self.menu.selected_item
        Clickable.handle_events(self, events)
        was_open = self.menu.is_open
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if self.hovered:
                    self.menu.is_open = True
                elif not self.menu.is_open and not self.is_click_on_farmable_zone(pos):
                    self.menu.is_open = False
                    self.menu.selected_item = None

        if self.menu.is_open and was_open:
            self.menu.handle_events(events)
        elif not self.menu.is_open and not was_open:
            if pygame.mouse.get_pressed(3)[0]:
                if selected_tool is not None:
                    pos = pygame.mouse.get_pos()
                    if selected_tool.type == FarmMenuItem.seed:
                        self.on_seed_planting(pos)
                    elif selected_tool.type == FarmMenuItem.recolter:
                        self.on_recolt(pos)
                    elif selected_tool.type == FarmMenuItem.water:
                        self.on_watering(pos)

    def update(self, camera_rect):
        GameObject.update(self, camera_rect)
        self.menu.update(camera_rect)
        for plant_loc in self.plants_location.values():
            plant_loc.update(camera_rect)
        for point in self.farm_zone:
            point.update(camera_rect)

    def draw(self, win, debug=False):
        selected_tool = self.menu.selected_item
        for plant in self.plants_location.values():
            plant.draw(win)
        GameObject.draw(self, win)
        if self.menu.is_open:
            self.menu.draw(win)
        # draw cursor tool
        if selected_tool is not None:
            img = selected_tool.zoom_buffer
            win.blit(img, img.get_rect(center=pygame.mouse.get_pos()))

        points = [p.coords for p in self.farm_zone]
        if debug:
            pygame.draw.polygon(win, RED, points, 2)

    def is_click_on_farmable_zone(self, pos):
        points = [p.coords for p in self.farm_zone]
        return is_point_inside_polygon(points, pos)

    def get_plant_at_pos(self, pos):
        plant_id = self.get_plant_spot_id_at(pos)
        if plant_id is None:
            return None
        return self.plants_location[plant_id].plant

    # ____ON EVENTS____#
    def on_seed_planting(self, pos):
        spot_id = self.get_plant_spot_id_at(pos)
        if spot_id is None:
            return
        if self.plants_location[spot_id].plant is not None:
            return
        if "fire" in self.menu.selected_item.name:
            plant = Plant("fire", self.plants_location[spot_id])
        elif "water" in self.menu.selected_item.name:
            plant = Plant("water", self.plants_location[spot_id])
        elif "ice" in self.menu.selected_item.name:
            plant = Plant("ice", self.plants_location[spot_id])
        else:
            raise Exception(f"Plant {self.menu.selected_item.name} not found")
        self.add_plant_at_id(spot_id, plant)

    def on_watering(self, pos):
        plant_id = self.get_plant_spot_id_at(pos)
        if plant_id is None:
            return
        plant = self.plants_location[plant_id].plant
        if plant is not None:
            plant.water()

    def on_recolt(self, pos):
        plant = self.get_plant_at_pos(pos)
        if not plant:
            return
        if plant is not None and plant.is_ready_to_harvest():
            item = plant.get_item()
            self.farm_inventory.add_item(item)
            plant.recolt()

    # ____SAVE____#
    def dump(self):
        """ Dump all the data of the farm to a json file to keep the farm state """
        data = {"plants": [plant.dump() for plant in self.plants_location.values()], }

        return data

    def load(self, data):
        """ Load the farm state from a json file """
        for plants_data in data["plants"]:
            plant_id = plants_data["id"]
            if plants_data["plant"]:
                plant_type = plants_data["plant"]["type"]
                img_index = plants_data["plant"]["development_index"]
                plant = Plant(plant_type, self.plants_location[plant_id], development_index=img_index)
                self.add_plant_at_id(plant_id, plant)


class PlantSpot(GameObject_no_img):
    counter = 0

    def __init__(self, pos):
        super().__init__(pos, (TILE_SIZE, TILE_SIZE))
        self.plant = None
        self.id = PlantSpot.counter
        PlantSpot.counter += 1

    def add_plant(self, plant):
        self.plant = plant

    def remove_plant(self):
        self.plant = None

    def update(self, camera_rect):
        GameObject_no_img.update(self, camera_rect)
        if self.plant is not None:
            self.plant.update(camera_rect)

    def draw(self, win):
        if self.plant is not None:
            win.blit(self.plant.zoom_buffer, self.plant.zoom_buffer.get_rect(midbottom=self.rect.midbottom))

    def dump(self):
        """
        Dump the plant spot data to a json file
        """
        return {"id": self.id, "plant": self.plant.dump() if self.plant is not None else None, }


class Plant:
    def __init__(self, plant_type, spot, development_index=0):
        self.development_index = development_index
        self.max_development_index = len(imgs.plants[plant_type]) - 1
        self.type = plant_type  # Fire, Water, Ice
        self.imgs = imgs.plants[plant_type]
        self.spot = spot

        max_widht = TILE_SIZE * 1.5
        for i in range(len(self.imgs)):
            if self.imgs[i].get_width() > max_widht:
                self.imgs[i] = scale_img(self.imgs[i], max_widht / self.imgs[i].get_width())
        self.zoom_buffer = self.imgs[self.development_index]

    def is_ready_to_harvest(self):
        return self.development_index == self.max_development_index

    def water(self):
        if self.development_index < len(self.imgs) - 1:
            self.development_index += 1

    def update(self, camera_rect):
        w, h = pygame.display.get_surface().get_size()
        zoom = 1 / (camera_rect.w / w)
        self.zoom_buffer = scale_img(self.imgs[self.development_index], zoom)

    def dump(self):
        return {"type": self.type,
                "development_index": self.development_index}

    def recolt(self):
        self.spot.plant = None

    def get_item(self):
        if self.type == "fire":
            return Item("fire", imgs.fire_seeds)
        elif self.type == "fire":
            return Item("fire", imgs.water_seeds)
        elif self.type == "fire":
            return Item("fire", imgs.ice_seeds)
        else:
            raise Exception(f"Plant type {self.type} not found")


def scale_img(img, zoom):
    return pygame.transform.scale(img, (int(img.get_width() * zoom), int(img.get_height() * zoom)))
