import pygame
from PygameUIKit import button
from pygame import Color

from test_game.backend.shop import Shop
from test_game.boring import utils
from test_game.frontend.ui_manager import UIElement


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
                                                      Color("green"),
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

        label = utils.render(item.name, self.font, gfcolor=Color("black"), ocolor=Color("white"), opx=1)
        window.blit(label, label.get_rect(center=img_rect.center))

        # Price
        label = utils.render(str(item.price), self.font, gfcolor=Color("black"), ocolor=Color("white"), opx=0)
        window.blit(label, label.get_rect(bottomright=img_rect.bottomright))

    def _handle_event(self, event):
        for btn in self.buy_buttons:
            btn.handle_event(event)
