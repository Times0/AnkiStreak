import pygame
import os


def clamp(n, minn, maxn):
    if n < minn:
        return minn
    elif n > maxn:
        return maxn
    else:
        return n


def is_point_inside_polygon(polygon_points, position):
    n = len(polygon_points)
    inside = False

    p1x, p1y = polygon_points[0]
    for i in range(n + 1):
        p2x, p2y = polygon_points[i % n]
        if position[1] > min(p1y, p2y):
            if position[1] <= max(p1y, p2y):
                if position[0] <= max(p1x, p2x):
                    if p1y != p2y:
                        x_intersection = (position[1] - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or position[0] <= x_intersection:
                            inside = not inside
        p1x, p1y = p2x, p2y

    return inside


def draw_menu_rect(win, rect, main_color):
    """Draw a rectangle with rounded corners with alpha transparency and a border"""
    pygame.draw.rect(win, main_color, rect, border_radius=10)
    pygame.draw.rect(win, (0, 0, 0), rect, 2, border_radius=10)


def nlerp(a, b, t, f):
    return a + (b - a) * f(t)
