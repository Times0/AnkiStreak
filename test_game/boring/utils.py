import pygame


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


def speed_func(x):
    """
    Magic function to compute the speed of the plant made by the great GPT4
    """
    return (3 * x ** 2 - 2 * x ** 3) ** 4


def render_multiples_texts(win, renders):
    x = 10
    for render in renders:
        win.blit(render, (x, 10))
        x += render.get_width()


_circle_cache = {}


def _circlepoints(r):
    r = int(round(r))
    if r in _circle_cache:
        return _circle_cache[r]
    x, y, e = r, 0, 1 - r
    _circle_cache[r] = points = []
    while x >= y:
        points.append((x, y))
        y += 1
        if e < 0:
            e += 2 * y - 1
        else:
            x -= 1
            e += 2 * (y - x) - 1
    points += [(y, x) for x, y in points if x > y]
    points += [(-x, y) for x, y in points if x]
    points += [(x, -y) for x, y in points if y]
    points.sort()
    return points


def render(text, font, gfcolor=pygame.Color('dodgerblue'), ocolor=(255, 255, 255), opx=2):
    """
    Render a text with a glow effect
    :param text:
    :param font:
    :param gfcolor:  glow color
    :param ocolor:  text color
    :param opx:  outline size
    :return:  pygame.Surface
    """
    textsurface = font.render(text, True, gfcolor).convert_alpha()
    w = textsurface.get_width() + 2 * opx
    h = font.get_height()

    osurf = pygame.Surface((w, h + 2 * opx)).convert_alpha()
    osurf.fill((0, 0, 0, 0))

    surf = osurf.copy()

    osurf.blit(font.render(text, True, ocolor).convert_alpha(), (0, 0))

    for dx, dy in _circlepoints(opx):
        surf.blit(osurf, (dx + opx, dy + opx))

    surf.blit(textsurface, (opx, opx))
    return surf
