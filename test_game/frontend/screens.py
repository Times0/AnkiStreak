import pygame
from PygameUIKit import button

from test_game.backend.inventory import Inventory
from test_game.backend.shop import Shop
from test_game.boring import colors, utils
from test_game.frontend.ui_manager import UIElement


class InventoryUI(UIElement):
    def __init__(self, inventory, manager):
        super().__init__("inventory", rect=pygame.Rect(0, 0, 300, 600), manager=manager)
        self.border_radius = 15  # Border radius of the inventory/inventoryUI
        self.item_spacing = 10  # Spacing between inventory items

        self.inventory_items: Inventory = inventory

    def _draw(self, win):
        x, y = self.rect.topleft
        width, height = self.rect.size
        # Draw the inventory items
        item_x = x + self.border_radius  # X position of the first item
        item_y = y + self.border_radius  # Y position of the first item

        for item_name, nb in self.inventory_items.items.items():
            # Draw each item as a rounded rectangle
            pygame.draw.rect(win, (76, 76, 76), (item_x, item_y, width - 2 * self.border_radius, 50),
                             border_radius=5)

            # Draw a subtle gradient on the item rectangle
            gradient_rect = pygame.Rect(item_x, item_y, width - 2 * self.border_radius, 50)
            gradient = pygame.Surface((gradient_rect.width, gradient_rect.height))
            pygame.draw.rect(gradient, (100, 100, 100), gradient.get_rect(top=1, bottom=gradient_rect.height - 2))
            pygame.draw.rect(gradient, (66, 66, 66), gradient.get_rect(top=0, bottom=1))
            pygame.draw.rect(win, (0, 0, 0), gradient_rect)
            win.blit(gradient, gradient_rect)

            # Draw the item image and number on the same line
            font = pygame.font.Font(None, 24)
            img = self.inventory_items.get_image(item_name)
            # resize the image to fit the item rectangle
            img = pygame.transform.scale(img, (40, 40))

            win.blit(img, (item_x + 5, item_y + 5))

            text = font.render(str(nb), True, (255, 255, 255))
            win.blit(text, (item_x + 50, item_y + 5))

            # Update the item Y position for the next item
            item_y += 60  # Adjust the spacing between items

    def _handle_event(self, events):
        pass


class ShopUI(UIElement):
    def __init__(self, shop, manager):
        super().__init__("shop", rect=pygame.Rect(0, 0, 700, 200), manager=manager)
        self.shop: Shop = shop

        # Position of the shopUI
        self.border_radius = 15  # Border radius of the shopUI
        self.item_spacing = 50  # Spacing between shopUI items

        # Calculate the width and height of each cell based on the size of the grid
        self.cell_width = 100
        self.cell_height = 100

        self.font = pygame.font.SysFont("Arial", 15, bold=True)

        self.buy_buttons: list[button.ButtonText] = []
        self.init_buy_buttons()

    def init_buy_buttons(self):
        for item_name, item in self.shop.items.items():
            f = lambda i=item: self.shop.buy(i)  # Very important to use = in lambda for variable scope (idk why)
            self.buy_buttons.append(button.ButtonText("Buy",
                                                      f,
                                                      colors.GREEN,
                                                      border_radius=5,
                                                      font=self.font))

    def _draw(self, window):
        x, y = self.rect.topleft
        # Draw the shop items
        item_x = x + self.border_radius  # X position of the first item
        item_y = y + self.border_radius  # Y position of the first item

        for i, (item_name, item) in enumerate(self.shop.items.items()):
            item_rect = pygame.Rect(item_x, item_y, self.cell_width, self.cell_height)
            self.draw_item(window, item, item_x, item_y)
            self.buy_buttons[i].draw(window, *self.buy_buttons[i].surface.get_rect(
                midtop=item_rect.midbottom).topleft)
            item_x += self.cell_width + self.item_spacing  # Adjust the spacing between items

    def draw_item(self, window, item, x, y):
        img = pygame.transform.scale(item.img, (self.cell_width - 10, self.cell_height - 10))
        img_rect = img.get_rect(topleft=(x, y))

        # Draw the item rectangle
        pygame.draw.rect(window, (76, 76, 76), (x, y, self.cell_width, self.cell_height),
                         border_radius=5)

        # Draw a subtle gradient on the item rectangle
        gradient_rect = pygame.Rect(x, y, self.cell_width, self.cell_height)
        gradient = pygame.Surface((gradient_rect.width, gradient_rect.height))
        pygame.draw.rect(gradient, (100, 100, 100), gradient.get_rect(top=1, bottom=gradient_rect.height - 2))
        pygame.draw.rect(gradient, (66, 66, 66), gradient.get_rect(top=0, bottom=1))
        pygame.draw.rect(window, (0, 0, 0), gradient_rect)

        window.blit(gradient, gradient_rect)
        window.blit(img, img_rect)

        label = utils.render(item.name, self.font, gfcolor=colors.BLACK, ocolor=colors.WHITE, opx=1)
        window.blit(label, label.get_rect(center=img_rect.center))

        # Price
        label = utils.render(str(item.price), self.font, gfcolor=colors.BLACK, ocolor=colors.WHITE, opx=0)
        window.blit(label, label.get_rect(bottomright=img_rect.bottomright))

    def _handle_event(self, event):
        for btn in self.buy_buttons:
            btn.handle_event(event)


class Popup(UIElement):
    def __init__(self, title, text):
        super().__init__(title, rect=pygame.Rect(0, 0, 300, 200))
        self.text = text
        self.font = pygame.font.SysFont("Arial", 30)

    def draw(self, window):
        x, y = self.rect.topleft
        width, height = self.rect.size
        # Draw the text
        text = utils.render(self.text, self.font, gfcolor=colors.WHITE, ocolor=colors.BLACK, opx=1)
        window.blit(text, text.get_rect(center=(x + width // 2, y + height // 2)))

    def handle_events(self, events):
        super().handle_events(events)
