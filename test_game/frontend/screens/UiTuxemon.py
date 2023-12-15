import random
from typing import Optional

import pygame
from PygameUIKit import button
from pygame import Color

from test_game.backend.tuxemons import Tuxemon, TuxemonInventory
from test_game.boring import imgs, config
from test_game.boring import utils
from test_game.frontend.screens.utils import Hoverable
from test_game.frontend.ui_manager import UIElement
from test_game.frontend.utils import draw_transparent_rect


class TuxemonCard(Hoverable):
    ANIMATION_FPS = 5

    def __init__(self, tux: Tuxemon, rect: pygame.Rect, offset=10):
        super().__init__(rect, inflate=5)
        self.offset = offset
        self.tuxemon = tux
        self.imgs = [tux.imgs["menu01"], tux.imgs["menu02"]]
        # Make the animation start at a random frame to make the cards look more alive
        self.time_since_last_img = random.random() * (1 / self.ANIMATION_FPS)
        self.frame_index = 0

        self.color = tux.favorite_color()

    def update(self, dt):
        # handle animation
        self.time_since_last_img += dt
        fps = 5
        if self.time_since_last_img > 1 / fps:
            self.time_since_last_img = 0
            self.frame_index = (self.frame_index + 1) % len(self.imgs)

    def draw(self, surface: pygame.Surface, pos):
        self.rect.center = pos
        rect = self.rect.copy()
        draw_transparent_rect(surface, rect, self.color, 150, border_radius=10)
        imgs = self.tuxemon.imgs["menu01"], self.tuxemon.imgs["menu02"]
        img = imgs[self.frame_index]
        img = pygame.transform.scale(img, (rect.width - self.offset * 2, rect.height - self.offset * 2))
        surface.blit(img, rect.inflate(-self.offset * 2, -self.offset * 2))

    def handle_event(self, event):
        super().handle_event(event)


class TuxemonUI(UIElement):
    def __init__(self, tuxemon_inventory: TuxemonInventory, manager):
        super().__init__("tuxemon", rect=pygame.Rect(0, 0, 300, 400), manager=manager)
        self.second_part_rect = self.rect.copy()
        self.second_part_rect.x += self.rect.width
        self.second_part_rect.width = 400
        self.tuxemons_inventory = tuxemon_inventory
        self.cards: list[TuxemonCard] = []

        self.expanded = False
        self.focused_card: Optional[TuxemonCard] = None
        self.init_cards()

        self.btn_feed = button.ButtonText("Feed", NotImplemented, Color("green"), border_radius=5,
                                          font_color=Color("black"),
                                          font=pygame.font.SysFont("Arial", 15))

        self.tuxemons_images_big = {}  # key is tuxemon name and value is the image
        self.fruits_images = {}

        # rects
        # Tuxeomons part
        self.tuxemon_part_rect = self.second_part_rect.copy()
        self.tuxemon_part_rect.height = 300
        self.tuxemon_part_rect.topleft = self.second_part_rect.topleft

        # Bottom right part
        bottomright_rect = self.second_part_rect.copy()
        bottomright_rect.y = self.tuxemon_part_rect.bottom
        bottomright_rect.height = self.second_part_rect.height - self.tuxemon_part_rect.height
        self.bottomright_rect = bottomright_rect

    def init_cards(self):
        self.cards = []
        for i, tuxemon in enumerate(self.tuxemons_inventory):
            card = TuxemonCard(tuxemon, pygame.Rect(0, 0, 80, 80))
            self.cards.append(card)
            for evolution in tuxemon.get_evolution_chain():
                img = evolution.imgs["front"]
                img = imgs.scale(img, (self.rect.width - 40, self.rect.height - 40))
                self.tuxemons_images_big[evolution.name] = img
            self.fruits_images[tuxemon.favorite_fruit()] = imgs.scale(imgs.items[tuxemon.favorite_fruit()], (30, 30))

    def _draw(self, win):
        if len(self.cards) != len(self.tuxemons_inventory.tuxemons):
            self.init_cards()

        card_size = 80
        margin = 15
        start = self.rect.move(margin + card_size / 2, margin + card_size / 2).topleft

        items_per_row = max(1, (self.rect.width - margin * 2) // card_size)
        item_spacing = (self.rect.width - margin * 2 - card_size * items_per_row) // (items_per_row - 1)

        row = 0
        col = 0
        for i, card in enumerate(self.cards):
            card.draw(win, (start[0] + col * (card_size + item_spacing),
                            start[1] + row * (card_size + item_spacing)))
            col += 1
            if col >= 3:
                col = 0
                row += 1

        if self.expanded:
            self.draw_tuxemon_view(win)

    def draw_tuxemon_view(self, win):
        """
        Only displayes the focused big_tuxemon when expanded
        """

        if config.DEBUG:
            pygame.draw.rect(win, Color("red"), self.tuxemon_part_rect, 5)
            pygame.draw.rect(win, Color("blue"), self.bottomright_rect, 5)

        # Draw separator
        pygame.draw.line(win, Color("black"), (self.tuxemon_part_rect.left, self.rect.top),
                         (self.tuxemon_part_rect.left, self.rect.bottom), 5)

        # Draw big big_tuxemon
        big_tuxemon = self.focused_card.tuxemon
        img = self.tuxemons_images_big[big_tuxemon.name]
        win.blit(img, img.get_rect(center=self.tuxemon_part_rect.center))

        # Draw tuxemon level on top left
        text = f"Level {big_tuxemon.level}"
        label = utils.render(text, pygame.font.SysFont("Arial", 15, bold=True), gfcolor=Color("white"),
                             ocolor=Color("black"), opx=1)
        win.blit(label, label.get_rect(center=(self.tuxemon_part_rect.left + 40, self.tuxemon_part_rect.top + 20)))

        # Draw vertical health bar with label xp : x/x
        off = 30
        x = self.tuxemon_part_rect.right - 40
        y1 = self.tuxemon_part_rect.top + off
        y2 = self.tuxemon_part_rect.bottom - off
        width_health_bar = 10

        pygame.draw.rect(win, Color(big_tuxemon.favorite_color()), (x, y1, width_health_bar, y2 - y1), 2,
                         border_radius=5)
        percentage = big_tuxemon.xp / big_tuxemon.max_xp()
        pygame.draw.rect(win, big_tuxemon.favorite_color(), (x, y2 - (y2 - y1) * percentage,
                                                             width_health_bar, (y2 - y1) * percentage), border_radius=5)

        text = f"{big_tuxemon.xp}/{big_tuxemon.max_xp()}"
        label = utils.render(text, pygame.font.SysFont("Arial", 15, bold=True), gfcolor=Color("white"),
                             ocolor=Color("black"), opx=1)
        win.blit(label, label.get_rect(center=(x, y2 + 10)))

        text = "Evolve-Progress"
        label = utils.render(text, pygame.font.SysFont("Arial", 15, bold=True), gfcolor=Color("white"),
                             ocolor=Color("black"), opx=1)
        win.blit(label, label.get_rect(center=(x, y1 - 10)))

        # Drw tuxemon name
        text = big_tuxemon.name
        label = utils.render(text, pygame.font.SysFont("Arial", 40),
                             gfcolor=Color(big_tuxemon.favorite_color()),
                             ocolor=Color("black"), opx=1)
        win.blit(label, label.get_rect(midtop=(self.tuxemon_part_rect.centerx, self.tuxemon_part_rect.top + 10)))
        # Draw button to feed the big_tuxemon
        surf = self.btn_feed.surface
        pos = surf.get_rect(center=self.bottomright_rect.center).topleft
        self.btn_feed.draw(win, *pos)

        # Draw big_tuxemon favorite fruit and number of fruits
        fruit_image = self.fruits_images[big_tuxemon.favorite_fruit()]
        win.blit(fruit_image, (pos[0] + surf.get_width() + 10, pos[1]))

        # Draw the number of fruits in the inventory
        nb = self.tuxemons_inventory.inventory.get(big_tuxemon.favorite_fruit(), 0)
        text = f"x{nb}"
        label = utils.render(text, pygame.font.SysFont("Arial", 15, bold=True), gfcolor=Color("white"),
                             ocolor=Color("black"), opx=1)
        win.blit(label, label.get_rect(center=(
            pos[0] + surf.get_width() + 10 + fruit_image.get_width() + 10, pos[1] + fruit_image.get_height() / 2)))

    def _handle_event(self, event):
        for card in self.cards:
            card.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for card in self.cards:
                if card.rect.collidepoint(event.pos):
                    self.expand(card)

        if self.expanded:
            self.btn_feed.handle_event(event)

    def expand(self, card: TuxemonCard):
        if card == self.focused_card:
            return
        if self.expanded:
            self.deexpand()
        self.expanded = True
        self.focused_card = card
        self.re_compute()

    def deexpand(self):
        if not self.expanded:
            return
        self.expanded = False
        self.focused_card = None
        self.re_compute()

    def re_compute(self):
        if self.expanded:
            self.rect.width += self.second_part_rect.width
            self.btn_feed.onclick_f = lambda: self.tuxemons_inventory.feed_tuxemon(self.focused_card.tuxemon.id)
        else:
            self.rect.width -= self.second_part_rect.width

        # center
        self.rect.center = self.manager.rect.center
        self.second_part_rect.topright = self.rect.topright
        self.tuxemon_part_rect.topright = self.second_part_rect.topright
        self.bottomright_rect.midtop = self.tuxemon_part_rect.midbottom

        self.require_update = True
        self.instantiate_button_cross()

    def _close(self):
        self.deexpand()

    def _update(self, dt):
        for card in self.cards:
            card.update(dt)
