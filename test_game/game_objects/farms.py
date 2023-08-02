import pygame

from test_game import objects
from test_game.boring import imgs, utils, colors
from test_game.boring.config import TILE_SIZE
from test_game.game_objects.inventory import Inventory
from test_game.game_objects.items import Item


class FarmMenuItem(Item):
    seed = 0
    recolter = 1
    water = 2

    def __init__(self, name, img, type):
        super().__init__(name, img)
        self.type = type


class Menu(objects.GameObject_no_img):
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

        self.inventory = None

        self.update_items_rect()

    def link_inventory(self, inventory):
        self.inventory = inventory

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

    def update_camera(self, camera_rect):
        objects.GameObject_no_img.update_camera(self, camera_rect)
        for i, item in enumerate(self.items):
            item.update_camera(camera_rect)
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
        # draw inventoryUI background slightly transparent black with white border
        utils.draw_menu_rect(win, self.rect, colors.MENU_BACKGROUND)
        for i, item in enumerate(self.items):
            if self.hovered_item_index == i:
                pygame.draw.rect(win, colors.MENU_SELECTED, self.items_rects[i].inflate(10, 10), border_radius=10)
            img = item.zoom_buffer
            if item.type == FarmMenuItem.seed and item not in self.inventory:
                # make img black and white
                img = utils.grayscale(img)
            win.blit(img, self.items_rects[i])


ice_seeds = FarmMenuItem("ice seeds", imgs.ice_seeds, type=FarmMenuItem.seed)
water_seeds = FarmMenuItem("water seeds", imgs.water_seeds, type=FarmMenuItem.seed)
fire_seeds = FarmMenuItem("fire seeds", imgs.fire_seeds, type=FarmMenuItem.seed)
bucket = FarmMenuItem("bucket", imgs.bucket, FarmMenuItem.water)
faux = FarmMenuItem("faux", imgs.faux, FarmMenuItem.recolter)

menu_items = [ice_seeds, water_seeds, fire_seeds, faux, bucket]


class Farm(objects.GameObject, objects.Clickable):
    def __init__(self, pos, size, img, farm_zone, name="Farm", inventory=None):
        objects.GameObject.__init__(self, pos, size, img)
        objects.Clickable.__init__(self, pos, size)
        self.menu = Menu(self, (66 * len(menu_items), 75), menu_items)
        self.plants_location: dict[int, PlantSpot] = {}
        self.farm_zone: list[objects.PointWithZoom] = farm_zone
        self.name = name
        self.farm_inventory: Inventory = inventory

        self.on_the_move_plants: list[OnTheMoveItem] = []

    def link_inventory(self, inventory: Inventory):
        self.farm_inventory = inventory
        self.menu.link_inventory(inventory)

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

    def add_plant_at_id(self, plant_id, plant):
        self.plants_location[plant_id].add_plant(plant)

    def remove_plant_at_id(self, plant_id):
        self.plants_location[plant_id].remove_plant()

    def handle_events(self, events):
        selected_tool = self.menu.selected_item
        objects.Clickable.handle_events(self, events)
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

    def update_camera(self, camera_rect):
        self.camera_rect = camera_rect
        objects.GameObject.update_camera(self, camera_rect)
        self.menu.update_camera(camera_rect)
        for plant_loc in self.plants_location.values():
            plant_loc.update_camera(camera_rect)
        for point in self.farm_zone:
            point.update_camera(camera_rect)

        for plant in self.on_the_move_plants:
            plant.update_camera(camera_rect)

    def draw(self, win, debug=False):
        selected_tool = self.menu.selected_item
        for plant in self.plants_location.values():
            plant.draw(win)
        objects.GameObject.draw(self, win)
        if self.menu.is_open:
            self.menu.draw(win)
        # draw cursor tool
        if selected_tool is not None:
            img = selected_tool.zoom_buffer
            win.blit(img, img.get_rect(center=pygame.mouse.get_pos()))

        points = [p.coords for p in self.farm_zone]
        if debug:
            pygame.draw.polygon(win, colors.RED, points, 2)

        for plant in self.on_the_move_plants:
            plant.draw(win)

    def is_click_on_farmable_zone(self, pos):
        points = [p.coords for p in self.farm_zone]
        return utils.is_point_inside_polygon(points, pos)

    def get_plantspot_at_pos(self, pos):
        plant_id = self.get_plant_spot_id_at(pos)
        if plant_id is None:
            return None
        return self.plants_location[plant_id]

    def water_all(self):
        for plant_loc in self.plants_location.values():
            if plant_loc.plant is not None:
                plant_loc.plant.water()

    def consume_seed(self, seed_type):
        if self.farm_inventory is None:
            raise Exception("No inventory linked to farm")
        itemname = seed_type + " seeds"
        if not itemname in self.farm_inventory.items:
            self.menu.selected_item = None
        else:
            self.farm_inventory.consume_item(itemname, 1)

    # ____ON EVENTS____#

    def on_seed_planting(self, pos):
        spot_id = self.get_plant_spot_id_at(pos)
        if spot_id is None or self.plants_location[spot_id].plant is not None:
            return

        plant_types = ["fire", "water", "ice"]
        for plant_type in plant_types:
            if plant_type in self.menu.selected_item.name:
                plant = Plant(plant_type, self.plants_location[spot_id])
                self.add_plant_at_id(spot_id, plant)
                self.consume_seed(plant_type)
                break
        else:
            raise Exception(f"Plant {self.menu.selected_item.name} not found")

    def on_watering(self, pos):
        plant_id = self.get_plant_spot_id_at(pos)
        if plant_id is None:
            return
        plant = self.plants_location[plant_id].plant
        if plant is not None:
            plant.water()

    def on_recolt(self, pos):
        plantspot = self.get_plantspot_at_pos(pos)
        if plantspot is None:
            return
        plant = plantspot.plant
        if not plant:
            return
        if plant is not None and plant.is_ready_to_harvest():
            vec_pos = pygame.math.Vector2(plantspot.pos)
            vec_dest = pygame.math.Vector2(self.camera_rect.move(-50, +50).topright)
            item_on_the_move = plant.get_item()
            self.on_the_move_plants.append(OnTheMoveItem(item_on_the_move, vec_pos, vec_dest))
            item = plant.get_item()
            self.farm_inventory.add_item(item)
            plant.recolt()

    def update(self, dt):
        for plant in self.on_the_move_plants:
            plant.update(dt)
            if plant.is_arrived:
                self.on_the_move_plants.remove(plant)

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


class OnTheMoveItem(objects.GameObject):
    def __init__(self, item: Item, pos, dest, speed_function=utils.speed_func):
        super().__init__(pos, item.size, item.img)
        self.item = item

        self.speed_function = speed_function
        self.dest = dest

        self.steps = []

        self.is_arrived = False
        self.index = 0

    def compute_steps(self, time=4):
        MAXFPS = 240
        pos = pygame.math.Vector2(self.pos)
        positions = []
        steps = int(time * MAXFPS)
        for i in range(steps + 1):
            t = i / steps
            positions.append(pos.lerp(self.dest, self.speed_function(t)))

        return positions

    def update(self, dt):
        if not self.steps:
            self.steps = self.compute_steps()
        MAXFPS = 240
        if self.steps:

            self.pos = self.steps[self.index]
            self.index += int(dt * MAXFPS / 1000)
            if self.index >= len(self.steps):
                self.is_arrived = True


class PlantSpot(objects.GameObject_no_img):
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

    def update_camera(self, camera_rect):
        objects.GameObject_no_img.update_camera(self, camera_rect)
        if self.plant is not None:
            self.plant.update_camera(camera_rect)

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

        self.last_zoom = 1
        self.requires_update = True

    def is_ready_to_harvest(self):
        return self.development_index == self.max_development_index

    def water(self):
        if self.development_index < len(self.imgs) - 1:
            self.development_index += 1
            self.requires_update = True

    def update_camera(self, camera_rect):
        w, h = pygame.display.get_surface().get_size()
        zoom = 1 / (camera_rect.w / w)
        if not self.requires_update and zoom == self.last_zoom:
            return

        self.zoom_buffer = scale_img(self.imgs[self.development_index], zoom)
        self.last_zoom = zoom
        self.requires_update = False

    def dump(self):
        return {"type": self.type,
                "development_index": self.development_index}

    def recolt(self):
        self.spot.plant = None

    def get_item(self) -> Item:
        if self.type not in ["fire", "ice", "water"]:
            raise Exception(f"Plant type {self.type} not found")
        k = self.type + " fruit"
        return Item(k, imgs.items[k])


def scale_img(img, zoom):
    return pygame.transform.scale(img, (int(img.get_width() * zoom), int(img.get_height() * zoom)))
