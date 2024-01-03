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
        self.price_font = pygame.font.SysFont("Arial", 20)
        self.btn_font = load_font("farm_font.ttf", 30)

        self.buy_buttons: list[button.ButtonText] = []
        self.init_buy_buttons()

        self.scaled_images = {}
        self.coin_img = pygame.transform.scale(imgs.coin, (20, 20))

    def init_buy_buttons(self):
        for item_name, item in self.shop.items.items():
            self.buy_buttons.append(button.ButtonText("      ",
                                                      lambda i=item: self.shop.buy(i),
                                                      Color(124, 197, 96), border_radius=5,
                                                      font=self.btn_font,
                                                      )
                                    )

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
            text = self.price_font.render(str(item.price), True, Color("white"))
            text_rect = text.get_rect(midleft=btn.rect.midleft).move(5, 0)
            window.blit(text, text_rect)
            window.blit(self.coin_img, self.coin_img.get_rect(midleft=text_rect.midright).move(5, 0))

            item_x += self.cell_width

    def _handle_event(self, event):
        for btn in self.buy_buttons:
            btn.handle_event(event)
