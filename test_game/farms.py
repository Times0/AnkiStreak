import pygame
from objects import GameObject_no_img, GameObject, Clickable
from config import *
from colors import *
import imgs


class Item:
    def __init__(self, name, img):
        self.name = name
        self.img = img


class Menu(GameObject_no_img):
    def __init__(self, pos, size, items):
        super().__init__(pos, size)
        self.items = items
        self.is_open = False

        self.hovered_item_index = -1

        self.item_size = (50, 50)
        self.item_padding = 10

        self.items_rects = []
        self.init_rects()

    def init_rects(self):
        self.items_rects = []
        for i, item in enumerate(self.items):
            self.items_rects.append(
                pygame.Rect((self.rect.x + self.item_padding + i * (self.item_size[0] + self.item_padding),
                             self.rect.y + self.item_padding),
                            self.item_size))

    def add_item(self, item):
        self.items.append(item)

    def update(self, camera_rect):
        GameObject_no_img.update(self, camera_rect)
        self.init_rects()

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
                for i, item in enumerate(self.items):
                    if self.items_rects[i].collidepoint(event.pos):
                        print(f"Clicked {item.name}")

    def draw(self, win):
        if self.is_open:
            pygame.draw.rect(win, GREEN, self.rect)
            for i, item in enumerate(self.items):
                if self.hovered_item_index == i:
                    pygame.draw.rect(win, RED, self.items_rects[i], 2)
                else:
                    pygame.draw.rect(win, BLUE, self.items_rects[i], 2)
                win.blit(item.img, self.items_rects[i])


class Farm(GameObject, Clickable):
    def __init__(self, pos, size, img):
        GameObject.__init__(self, pos, size, img)
        Clickable.__init__(self, pos, size)
        self.menu = Menu((self.rect.x, self.rect.y - 50),
                         (200, 100),
                         [Item("Plant", imgs.img_plant1), Item("Plant2", imgs.img_plant2)])

    def handle_events(self, events):
        Clickable.handle_events(self, events)
        if self.menu.is_open:
            self.menu.handle_events(events)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.hovered:
                    self.menu.is_open = True

    def update(self, camera_rect):
        GameObject.update(self, camera_rect)
        self.menu.update(camera_rect)

    def draw(self, win):
        GameObject.draw(self, win)
        self.menu.draw(win)


class Plant(GameObject):
    def __init__(self, pos, farm):
        GameObject.__init__(self, pos, (TILE_SIZE, TILE_SIZE), imgs.img_plant1)
        self.farm = farm

    def handle_events(self, events):
        for event in events:
            pass
