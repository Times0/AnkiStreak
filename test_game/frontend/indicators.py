import os

import pygame
from pygame import Rect

from test_game.boring import colors, utils, imgs
from test_game.frontend.ui_manager import UIElement

cwd = os.path.dirname(__file__)
font_title_path = os.path.join(cwd, "../assets", "fonts", "farm_font.ttf")
font_coins_path = os.path.join(cwd, "../assets", "fonts", "title.otf")


class Tooltip:
    def __init__(self, text, rect):
        self.rect = rect
        self._is_hovered = False
        self.text = text

    def _handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.on_hover()
            else:
                self.on_unhover()

    def on_hover(self):
        self._is_hovered = True

    def on_unhover(self):
        self._is_hovered = False

    def draw(self, surface):
        if not self._is_hovered:
            return
        x, y = self.rect.topleft
        width, height = self.rect.size
        # display the tooltip
        tooltip_text = self.text
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


class CardIndicators(UIElement, Tooltip):
    def __init__(self, manager,
                 color=(127, 255, 0), bg_color=(169, 169, 169), border_color=(0, 0, 0),
                 font_color=(0, 0, 0)):
        rect = pygame.Rect(40, 20, 200, 30)
        UIElement.__init__(self, "card_indicators", rect=rect, manager=manager, is_permament=True)
        Tooltip.__init__(self, "Cards learned today", rect)

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

    def _draw(self, surface):
        x, y = self.rect.topleft
        width, height = self.rect.size
        border_radius = 5
        border_thickness = 2

        # create the border
        pygame.draw.rect(surface, self.border_color, self.rect, border_radius=border_radius)

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
        font = pygame.font.Font(None, 24)
        text = f"{self.nb_cards_learned}/{self.nb_cards_total}"
        text_surface = font.render(text, True, self.font_color)
        text_rect = text_surface.get_rect(center=(x + width / 2, y + height / 2))
        surface.blit(text_surface, text_rect)

        # Draw the card image
        surface.blit(self.image, (x - 25, y - 10))

        Tooltip.draw(self, surface)

    def _handle_event(self, event):
        Tooltip._handle_event(self, event)


class CoinsIndicator(UIElement):
    def __init__(self, manager):
        rect = Rect(20, 100, 0, 0)
        UIElement.__init__(self, "coins_indicator", rect=rect, manager=manager, is_permament=True)
        self.nb_coins = 0
        self.image = imgs.coin
        self.image = pygame.transform.scale(self.image,
                                            (50, self.image.get_height() * 50 // self.image.get_width()))
        self.font = pygame.font.Font(font_coins_path, 45)

    def update_money(self, nb):
        self.nb_coins = nb

    def _draw(self, win):
        x, y = self.rect.topleft
        win.blit(self.image, (x, y))

        coin_text = utils.render(str(self.nb_coins), self.font, gfcolor=colors.WHITE, ocolor=colors.BLACK)

        coin_text_rect = coin_text.get_rect()  # get the rectangle that encloses the text
        text_y = y + self.image.get_height() // 2 - coin_text_rect.height // 2  # center the text vertically with respect to the coin image

        win.blit(coin_text, (x + self.image.get_width() + 10, text_y))

        self.rect = pygame.Rect(x, y, self.image.get_width() + 10 + coin_text_rect.width, self.image.get_height())

    def _handle_event(self, event):
        pass
