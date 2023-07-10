import os.path

import pygame

import colors
from farms import Inventory
from config import *


class InventoryUI:
    def __init__(self, inventory):
        self.is_open = False
        self.width = 300  # Width of the inventory/menu
        self.height = 400  # Height of the inventory/menu
        self.border_radius = 15  # Border radius of the inventory/menu
        self.item_spacing = 10  # Spacing between inventory items

        self.inventory_items: Inventory = inventory

    def draw(self, win):
        # Calculate the position of the inventory/menu at the center of the screen
        screen_width = pygame.display.Info().current_w
        screen_height = pygame.display.Info().current_h
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2

        # Draw the inventory/menu background
        pygame.draw.rect(win, (51, 51, 51), (x, y, self.width, self.height), border_radius=self.border_radius)

        # Draw the inventory items
        item_x = x + self.border_radius  # X position of the first item
        item_y = y + self.border_radius  # Y position of the first item

        for item_name, nb in self.inventory_items.items.items():
            # Draw each item as a rounded rectangle
            pygame.draw.rect(win, (76, 76, 76), (item_x, item_y, self.width - 2 * self.border_radius, 50),
                             border_radius=5)

            # Draw a subtle gradient on the item rectangle
            gradient_rect = pygame.Rect(item_x, item_y, self.width - 2 * self.border_radius, 50)
            gradient = pygame.Surface((gradient_rect.width, gradient_rect.height))
            pygame.draw.rect(gradient, (100, 100, 100), gradient.get_rect(top=1, bottom=gradient_rect.height - 2))
            pygame.draw.rect(gradient, (66, 66, 66), gradient.get_rect(top=0, bottom=1))
            pygame.draw.rect(win, (0, 0, 0), gradient_rect)
            win.blit(gradient, gradient_rect)

            # Draw the item image and number on the same line
            font = pygame.font.Font(None, 24)
            img = self.inventory_items.get_item_image(item_name)
            # resize the image to fit the item rectangle
            img = pygame.transform.scale(img, (40, 40))

            win.blit(img, (item_x + 5, item_y + 5))

            text = font.render(str(nb), True, (255, 255, 255))
            win.blit(text, (item_x + 50, item_y + 5))

            # Update the item Y position for the next item
            item_y += 60  # Adjust the spacing between items


class CardIndicators:
    def __init__(self):
        self.counter = 0

        self.font = pygame.font.Font(os.path.join(font_path_dir, "farm_font2.ttf"), 30)
        self.text_render = None
        self.text_render_2 = None
        self.text_render_3 = None

        self.render()

    def render(self):
        self.text_render = self.font.render("Keep learning, ", True, colors.BLACK)
        self.text_render_2 = self.font.render(f"{self.counter}/10 ", True, colors.RED)
        self.text_render_3 = self.font.render("cards learned today", True, colors.BLACK)

    def draw(self, win):
        renders = [self.text_render, self.text_render_2, self.text_render_3]
        total_width = sum([render.get_width() for render in renders])
        surf = pygame.Surface((total_width, self.text_render.get_height()), pygame.SRCALPHA)
        surf.fill((255, 255, 255, 100))
        win.blit(surf, (10, 10))

        render_multiples_texts(win, renders)


def render_multiples_texts(win, renders):
    x = 10
    for render in renders:
        win.blit(render, (x, 10))
        x += render.get_width()
