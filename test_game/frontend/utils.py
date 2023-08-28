import pygame as pg
from pygame import Surface, Rect, Color


def draw_transparent_rect(screen: Surface, rect: Rect, color: Color, alpha: int, border_radius=0):
    """
    Draw a transparent rectangle with rounded corners.
    :param screen:
    :param rect:
    :param color:
    :param alpha:
    :param border_radius:
    :return:
    """
    surf = pg.Surface(rect.size, pg.SRCALPHA)
    pg.draw.rect(surf, color, surf.get_rect().inflate(-1, -1), border_radius=border_radius)
    surf.set_alpha(alpha)
    screen.blit(surf, rect)
