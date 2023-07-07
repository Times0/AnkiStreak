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


seeds = FarmMenuItem("Seeds", imgs.seeds, FarmMenuItem.seed)
water_seeds = FarmMenuItem("Water Seeds", imgs.water_seeds, FarmMenuItem.seed)
fire_seeds = FarmMenuItem("Fire Seeds", imgs.fire_seeds, FarmMenuItem.seed)
bucket = FarmMenuItem("Bucket", imgs.bucket, FarmMenuItem.water)
faux = FarmMenuItem("Faux", imgs.faux, FarmMenuItem.recolter)
menu_items = [seeds, water_seeds, fire_seeds, bucket, faux]


class Farm(GameObject, Clickable):
    def __init__(self, pos, size, img, farm_zone):
        GameObject.__init__(self, pos, size, img)
        Clickable.__init__(self, pos, size)
        self.menu = Menu(self, (66 * len(menu_items), 75), menu_items)
        self.plants_location = []
        self.farm_zone: list[PointWithZoom] = farm_zone

    def add_plant_location(self, plant):
        self.plants_location.append(plant)

    def add_plant_at(self, pos):
        for plant_loc in self.plants_location:
            if plant_loc.rect.collidepoint(pos):
                if plant_loc.plant is not None:
                    return
                if self.menu.selected_item.name == "Fire Seeds":
                    plant_loc.add_plant(imgs.fire_plant)
                elif self.menu.selected_item.name == "Water Seeds":
                    plant_loc.add_plant(imgs.water_plant)
                elif self.menu.selected_item.name == "Ice Seeds":
                    plant_loc.add_plant(imgs.ice_plant)
                else:
                    return

    def remove_plant_at(self, pos):
        for plant_loc in self.plants_location:
            if plant_loc.rect.collidepoint(pos):
                plant_loc.remove_plant()
                break

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
            if pygame.mouse.get_pressed()[0]:
                if selected_tool is not None:
                    if selected_tool.type == FarmMenuItem.seed:
                        self.add_plant_at(pygame.mouse.get_pos())
                    elif selected_tool.type == FarmMenuItem.recolter:
                        self.remove_plant_at(pygame.mouse.get_pos())
                    elif selected_tool.type == FarmMenuItem.water:
                        self.water_plant_at(pygame.mouse.get_pos())

    def update(self, camera_rect):
        GameObject.update(self, camera_rect)
        self.menu.update(camera_rect)
        for plant_loc in self.plants_location:
            plant_loc.update(camera_rect)
        for point in self.farm_zone:
            point.update(camera_rect)

    def draw(self, win, debug=False):
        selected_tool = self.menu.selected_item
        for plant in self.plants_location:
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

    def water_plant_at(self, pos):
        for plant_loc in self.plants_location:
            if plant_loc.rect.collidepoint(pos):
                if plant_loc.plant is not None:
                    plant_loc.plant.water()


class PlantSpot(GameObject_no_img):
    def __init__(self, pos):
        super().__init__(pos, (TILE_SIZE, TILE_SIZE))
        self.plant = None

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



class Plant:
    def __init__(self, imgs):
        self.current_img_index = 0
        self.imgs = imgs

        max_widht = TILE_SIZE * 1.5

        for i in range(len(self.imgs)):
            if self.imgs[i].get_width() > max_widht:
                self.imgs[i] = scale_img(self.imgs[i], max_widht / self.imgs[i].get_width())
        self.zoom_buffer = self.imgs[self.current_img_index]

    def water(self):
        if self.current_img_index < len(self.imgs) - 1:
            self.current_img_index += 1

    def update(self, camera_rect):
        w, h = pygame.display.get_surface().get_size()
        zoom = 1 / (camera_rect.w / w)
        self.zoom_buffer = scale_img(self.imgs[self.current_img_index], zoom)


def scale_img(img, zoom):
    return pygame.transform.scale(img, (int(img.get_width() * zoom), int(img.get_height() * zoom)))
