import os

import pygame
from PygameUIKit import button

from test_game.backend.inventory import Inventory
from test_game.backend.shop import Shop
from test_game.boring import colors, utils
from test_game.boring import imgs
from test_game.frontend.ui_manager import UIElement

cwd = os.path.dirname(__file__)
font_title_path = os.path.join(cwd, "../assets", "fonts", "farm_font.ttf")
font_coins_path = os.path.join(cwd, "../assets", "fonts", "title.otf")


class UIObject:
    def __init__(self):
        self._is_visible = False
        self.rect = pygame.Rect(0, 0, 0, 0)

        self._is_hovered = False

    def toggle_visibility(self):
        self._is_visible = not self._is_visible

    def isVisible(self):
        return self._is_visible

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                if self.rect.collidepoint(event.pos):
                    self.on_hover()
                else:
                    self.on_unhover()

    def on_hover(self):
        self._is_hovered = True

    def on_unhover(self):
        self._is_hovered = False


# class GameWindow:
#     def __init__(self, title):
#         self.title = title
#         self._is_visible = False
#
#         self.title_offset = 85  # Offset of the title from the top left corner of the window
#
#         self.cross_img = imgs.cross
#         self.cross_img = pygame.transform.scale(self.cross_img, (50, 50))
#
#         self.rect = pygame.Rect(0, 0, 0, 0)
#         self.cross_rect = pygame.Rect(0, 0, 0, 0)
#
#         self.hovered = False
#
#     def draw_win(self, win, x, y, width, height, color=colors.BROWN, border_radius=15, center_title=False):
#         self.rect = pygame.Rect(x, y, width, height)
#         self.cross_rect = pygame.Rect(x + width - self.cross_img.get_width(),
#                                       y + 10 - self.title_offset + self.cross_img.get_height() / 3,
#                                       self.cross_img.get_width(),
#                                       self.cross_img.get_height())
#         pygame.draw.rect(win, color, (x, y, width, height),
#                          border_radius=border_radius)
#         # draw the title
#         font = pygame.font.Font(font_title_path, 75)
#         text = utils.render(self.title, font, gfcolor=colors.BLACK, ocolor=colors.WHITE, opx=2)
#
#         if center_title:
#             win.blit(text, (x + width / 2 - text.get_width() / 2, y + 10 - self.title_offset))
#         else:
#             win.blit(text, (x + 10, y + 10 - self.title_offset))
#
#         # draw cross
#         img = self.cross_img  # black cross
#         if self.hovered:
#             pygame.draw.rect(win, colors.RED_CROSS, self.cross_rect.inflate(10, 10), border_radius=5)
#             # change cross to WHITE
#             img = pygame.transform.scale(img, (50, 50))
#             win.blit(img, self.cross_rect)
#         else:
#             win.blit(img, self.cross_rect)
#
#     def toggle_visibility(self):
#         self._is_visible = not self._is_visible
#
#     def handle_events(self, events):
#         for event in events:
#             if event.type == pygame.MOUSEBUTTONDOWN:
#                 if event.button == 1:
#                     if self.cross_rect.collidepoint(event.pos):
#                         self.toggle_visibility()
#             elif event.type == pygame.MOUSEMOTION:
#                 if self.cross_rect.collidepoint(event.pos):
#                     self.on_hover()
#                 else:
#                     self.on_unhover()
#
#     def on_hover(self):
#         self.hovered = True
#
#     def on_unhover(self):
#         self.hovered = False
#
#     def isVisible(self):
#         return self._is_visible


class InventoryUI(UIElement):
    def __init__(self, inventory,manager):
        super().__init__("inventory", rect=pygame.Rect(200, 200, 500, 500),manager=manager)
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

    def handle_events(self, events):
        super().handle_events(events)


class ShopUI(UIElement):
    def __init__(self, shop):
        super().__init__("Shop", rect=pygame.Rect(200, 200, 500, 500))
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
            f = lambda i=item: self.shop.buy(
                i)  # Very important to use = in lambda for variable scope (no idea what im writing)
            self.buy_buttons.append(button.ButtonText("Buy",
                                                      f,
                                                      colors.GREEN,
                                                      border_radius=5,
                                                      font=self.font))

    def draw(self, window, x, y, width, height):
        self.draw_win(window, x, y, width, height)

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

    def handle_events(self, events):
        super().handle_events(events)
        for btn in self.buy_buttons:
            btn.handle_events(events)


class Popup(UIElement):
    def __init__(self, title, text):
        super().__init__(title)
        self._is_visible = True  # The popup is visible when created
        self.text = text

        self.font = pygame.font.SysFont("Arial", 30)

    def draw(self, window, x, y, width, height):
        self.draw_win(window, x, y, width, height)

        # Draw the text
        text = utils.render(self.text, self.font, gfcolor=colors.WHITE, ocolor=colors.BLACK, opx=1)
        window.blit(text, text.get_rect(center=(x + width // 2, y + height // 2)))

    def handle_events(self, events):
        super().handle_events(events)


class CardIndicators(UIObject):
    def __init__(self, color=(127, 255, 0), bg_color=(169, 169, 169), border_color=(0, 0, 0), font_color=(0, 0, 0)):
        super().__init__()
        self.is_visible = True
        self.nb_cards_learned = 0
        self.nb_cards_total = 10
        self.color = pygame.Color(*color)
        self.bg_color = pygame.Color(*bg_color)
        self.border_color = pygame.Color(*border_color)
        self.font_color = pygame.Color(*font_color)

        # Load the image
        self.image = imgs.card
        self.image = pygame.transform.scale(self.image, (50, self.image.get_height() * 50 // self.image.get_width()))

    def set_nb_cards_learned(self, nb):
        self.nb_cards_learned = nb

    def set_nb_cards_total(self, nb):
        self.nb_cards_total = nb

    def draw(self, surface, x, y, width, height):
        border_radius = 5
        self.rect = pygame.Rect(x, y, width, height)
        border_thickness = 2
        if not self.is_visible:
            return

        # create the border
        border_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, self.border_color, border_rect, border_radius=border_radius)

        # create the background rectangle
        bg_rect = pygame.Rect(x + border_thickness, y + border_thickness, width - 2 * border_thickness,
                              height - 2 * border_thickness)
        pygame.draw.rect(surface, self.bg_color, bg_rect, border_radius=border_radius)

        if self.nb_cards_total > 0:
            # calculate the length of the progress bar
            progress_ratio = min(self.nb_cards_learned / self.nb_cards_total, 1)  # limit the ratio to 1
            progress_length = int((width - 2 * border_thickness) * progress_ratio)

            # create the progress rectangle
            progress_rect = pygame.Rect(x + border_thickness,
                                        y + border_thickness,
                                        progress_length,
                                        height - 2 * border_thickness)
            pygame.draw.rect(surface, self.color, progress_rect, border_radius=border_radius)

        # display the number of learned cards to total cards
        font = pygame.font.Font(None, 24)  # select a font that fits your game's style
        text = f"{self.nb_cards_learned}/{self.nb_cards_total}"
        text_surface = font.render(text, True, self.font_color)
        text_rect = text_surface.get_rect(center=(x + width / 2, y + height / 2))
        surface.blit(text_surface, text_rect)

        # Draw the card image
        surface.blit(self.image, (x - 25, y - 10))

        if self._is_hovered:
            # display the tooltip
            tooltip_text = "Cards learned today"
            tooltip_font = pygame.font.Font(None, 25)  # select a font that fits your game's style
            tooltip_surface = tooltip_font.render(tooltip_text, True, colors.WHITE)
            tooltip_rect = tooltip_surface.get_rect(
                center=(x + width / 2, y + height + 40))  # adjust positioning as needed
            pygame.draw.rect(surface, colors.BROWN, tooltip_rect.inflate(15, 15))  # add a small padding
            surface.blit(tooltip_surface, tooltip_rect)

            # draw the tooltip arrow
            # draw the tooltip arrow
            arrow_points = [(x + width / 2, y + height + 5),
                            (x + width / 2 - 10, y + height + 5 + 10),
                            (x + width / 2 + 10, y + height + 5 + 10)]

            pygame.draw.polygon(surface, colors.BROWN, arrow_points)

            # draw the tooltip border
            pygame.draw.polygon(surface, colors.BLACK, arrow_points, width=1)
            pygame.draw.rect(surface, colors.BLACK, tooltip_rect.inflate(15, 15), width=1)


class CoinsIndicator(UIObject):
    def __init__(self):
        super().__init__()
        self.is_visible = True
        self.nb_coins = 0
        self.image = imgs.coin
        self.image = pygame.transform.scale(self.image,
                                            (50, self.image.get_height() * 50 // self.image.get_width()))
        self.font = pygame.font.Font(font_coins_path, 45)

        self.rect = pygame.Rect(0, 0, 0, 0)

    def update_money(self, nb):
        self.nb_coins = nb

    def draw(self, win, x, y, width, height):
        win.blit(self.image, (x, y))

        coin_text = utils.render(str(self.nb_coins), self.font, gfcolor=colors.WHITE, ocolor=colors.BLACK)

        coin_text_rect = coin_text.get_rect()  # get the rectangle that encloses the text
        text_y = y + self.image.get_height() // 2 - coin_text_rect.height // 2  # center the text vertically with respect to the coin image

        win.blit(coin_text, (x + self.image.get_width() + 10, text_y))

        self.rect = pygame.Rect(x, y, self.image.get_width() + 10 + coin_text_rect.width, self.image.get_height())
