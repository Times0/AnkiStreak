import pygame
import pygame as pg
from pygame import Surface, Rect, Color
from scipy.ndimage import gaussian_filter


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


def blit_acrylic_surface(screen_in, screen_out, pos, surface, blur_radius=5):
    """
    Blit une surface "acrylique" sur l'écran à la position spécifiée.

    screen: l'écran pygame sur lequel dessiner
    surface: la surface pygame à dessiner de manière acrylique
    position: la position à laquelle dessiner la surface
    blur_radius: le rayon du flou gaussien à appliquer
    """
    # Extraire la zone de l'arrière-plan où la surface sera dessinée

    bg_rect = pygame.Rect(pos, surface.get_size())
    bg_subsurface = screen_in.subsurface(bg_rect).copy()

    np_surface = pygame.surfarray.pixels3d(bg_subsurface).transpose((1, 0, 2))

    for i in range(3):  # Pour chaque canal R, G, B
        np_surface[..., i] = gaussian_filter(np_surface[..., i], sigma=blur_radius)

    blurred_subsurface = pygame.surfarray.make_surface(np_surface.transpose((1, 0, 2)))
    screen_out.blit(blurred_subsurface, (0, 0))
    screen_out.blit(surface, (0, 0))
