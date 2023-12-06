import pygame
from PygameUIKit import button
from PygameUIKit.button import ButtonText
from pygame import Color

from test_game.backend.shop import Shop
from test_game.boring import utils, imgs
from test_game.boring.imgs import load_font
from test_game.frontend.ui_manager import UIElement


class ShopUI(UIElement):
    def __init__(self, shop, manager):
        super().__init__("shop", rect=pygame.Rect(0, 0, 700, 200), manager=manager)
        self.shop: Shop = shop

        # Position of the shopUI
        self.border_radius = 15  # Border radius of the shopUI
        self.item_spacing = 0  # Spacing between shopUI items

        # Calculate the width and height of each cell based on the size of the grid
        self.cell_width = 700 // len(self.shop.items)
        self.cell_height = 100

        self.font = load_font("blomberg.otf", 20)
        self.btn_font = load_font("farm_font.ttf", 30)

        self.buy_buttons: list[button.ButtonText] = []
        self.init_buy_buttons()

        self.scaled_images = {}
        self.coin_img = pygame.transform.scale(imgs.coin, (20, 20))

    def init_buy_buttons(self):
        for item_name, item in self.shop.items.items():
            self.buy_buttons.append(button.ButtonText("      ",
                                                      lambda i=item: self.shop.buy(i),
                                                      Color("darkgreen"), border_radius=5,
                                                      font=self.btn_font))

    def _draw(self, window):
        x, y = self.rect.topleft
        # Draw the shop items
        item_x = x + self.cell_width // 2  # X position of the first item

        for i, (item_name, item) in enumerate(self.shop.items.items()):
            if item_name not in self.scaled_images:
                self.scaled_images[item_name] = pygame.transform.scale(item.img, (80, 80))
            item_y = y + self.border_radius  # Y position of the first item

            # Draw the item name
            nb = self.shop.inventory.items.get(item_name, 0)
            text = self.font.render(f"{item_name} ({nb})", True, Color("black"))
            text_rect = text.get_rect(midtop=(item_x, item_y))
            window.blit(text, text_rect)

            item_y += text_rect.height + 5

            # Draw the item image
            img = self.scaled_images[item_name]
            img_rect = img.get_rect(midtop=(item_x, item_y))
            window.blit(img, img_rect)

            # Draw the buy button under the item image
            btn: ButtonText = self.buy_buttons[i]
            btn.draw(window, *btn.surface.get_rect(midtop=(item_x, item_y + img_rect.height + 5)).topleft)
            # draw the price next to the buy button and the coin img
            text = self.font.render(str(item.price), True, Color("white"))
            text_rect = text.get_rect(midleft=btn.rect.midleft).move(5, 0)
            window.blit(text, text_rect)
            window.blit(self.coin_img, self.coin_img.get_rect(midleft=text_rect.midright).move(5, 0))

            item_x += self.cell_width

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
