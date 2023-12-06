import pygame
from pygame import Color

from test_game.backend.inventory import Inventory
from test_game.boring.imgs import load_font
from test_game.frontend.ui_manager import UIElement


class InventoryUI(UIElement):
    def __init__(self, inventory, manager):
        super().__init__("inventory", rect=pygame.Rect(0, 0, 300, 600), manager=manager)
        self.border_radius = 15  # Border radius of the inventory/inventoryUI
        self.item_spacing = 10  # Spacing between inventory items

        self.inventory_items: Inventory = inventory
        self.item_images_scaled = {}

        self.font = load_font("blomberg.otf", 20)
        self.small_font = load_font("title.otf", 30)

    def _draw(self, win):
        x, y = self.rect.topleft
        width, height = self.rect.size
        # Draw the inventory items
        item_x = x + self.border_radius  # X position of the first item
        item_y = y + self.border_radius  # Y position of the first item

        for item_name, nb in self.inventory_items.items.items():
            if item_name not in self.item_images_scaled:
                self.item_images_scaled[item_name] = pygame.transform.scale(self.inventory_items.get_image(item_name),
                                                                            (60, 60))
            # Draw the item row
            item_img = self.item_images_scaled[item_name]
            item_rect = item_img.get_rect()
            item_rect.topleft = item_x, item_y
            win.blit(item_img, item_rect)

            # Draw the item name
            text = self.font.render(item_name, True, Color("black"))
            text_rect = text.get_rect(midleft=item_rect.midright).move(30, 0)
            win.blit(text, text_rect)
            # draw line at the bottom of the row
            pygame.draw.line(win, Color("black"), (x, item_y + item_rect.height + 5),
                             (x + width, item_y + item_rect.height + 5))
            # Draw the item quantity
            text = self.small_font.render(str(nb), True, Color("black"))
            text_rect = text.get_rect(midright=(x + width - self.border_radius * 2, item_rect.centery))
            win.blit(text, text_rect)

            item_y += item_rect.height + self.item_spacing

    def _handle_event(self, events):
        pass
