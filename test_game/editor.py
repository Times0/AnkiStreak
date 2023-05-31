import tkinter.filedialog

import pygame
from constants import *

class Grid:
    def __init__(self, n, m):
        self.n = n
        self.m = m

    def draw(self, win, rect, draw_grid=False):
        if draw_grid:
            for i in range(self.n + 1):
                pygame.draw.line(win, WHITE, (rect.x, rect.y + i * rect.height / self.n), (rect.x + rect.width, rect.y + i * rect.height / self.n))
            for j in range(self.m + 1):
                pygame.draw.line(win, WHITE, (rect.x + j * rect.width / self.m, rect.y), (rect.x + j * rect.width / self.m, rect.y + rect.height))

class LevelEditor:
    def __init__(self, win):
        self.win = win
        self.grid = Grid(7, 7)

        self.game_objects = []
        self.game_is_on = True

        self.available_tiles =[]

        self.selected_tile = 0

        self.save_label = pygame.font.SysFont("arial", 30).render("Sauvegarder", True, BLACK)
        self.save_x, self.save_y = 100, 100

        self.load_label = pygame.font.SysFont("arial", 30).render("Charger", True, BLACK)
        self.load_x, self.load_y = 100, 200

        self.erase_label = pygame.font.SysFont("arial", 30).render("Effacer", True, BLACK)
        self.erase_x, self.erase_y = 500, 100

        self.dragging = False
        self.drag_start = None

    def run(self):
        clock = pygame.time.Clock()
        while self.game_is_on:
            dt = clock.tick(60)
            self.win.fill(DARKWHITE)
            self.events()
            self.draw(self.win)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_is_on = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                s_width, s_height = pygame.display.get_surface().get_size()
                w, h = 500, 500
                x0 = (s_width - w) // 2
                y0 = (s_height - h) // 2
                if x0 <= event.pos[0] <= x0 + w and y0 <= event.pos[1] <= y0 + h:
                    i = (event.pos[1] - y0) * self.grid.n // h
                    j = (event.pos[0] - x0) * self.grid.m // w
                    if self.available_tiles[self.selected_tile] == "mur":
                        self.grid.grid[i][j] = 1
                    elif self.available_tiles[self.selected_tile] == "vide":
                        self.grid.grid[i][j] = 0
                    elif self.available_tiles[self.selected_tile] == "bouton":
                        for obj in self.game_objects:
                            if obj.i == i and obj.j == j:
                                self.game_objects.remove(obj)
                                return
                        id_color = -1
                        for obj in self.game_objects:
                            if obj.type == "button":
                                id_color = max(id_color, obj.id_color)
                        id_color += 1

                        self.game_objects.append(Button(i, j, self.grid, id_color))

                    elif self.available_tiles[self.selected_tile] == "laser_door":
                        for obj in self.game_objects:
                            if obj.i == i and obj.j == j:
                                self.game_objects.remove(obj)
                                return
                        id_color = -1
                        for obj in self.game_objects:
                            if obj.type == "laser_door":
                                id_color = max(id_color, obj.id_color)
                        id_color += 1

                        self.dragging = True
                        self.drag_start = (i, j)

                if x0 + w + 10 <= event.pos[0] <= x0 + w + 10 + 50 and y0 <= event.pos[1] <= y0 + len(
                        self.available_tiles) * 100:
                    self.selected_tile = (event.pos[1] - y0) // 100
                # click on erase
                if self.erase_x <= event.pos[0] <= self.erase_x + self.erase_label.get_width() \
                        and self.erase_y <= event.pos[1] <= self.erase_y + self.erase_label.get_height():
                    print("erase")
                    n, m = self.grid.n, self.grid.m
                    self.grid = Grid(n, m)
                    self.game_objects = []

                # click on save
                if self.save_x <= event.pos[0] <= self.save_x + self.save_label.get_width() \
                        and self.save_y <= event.pos[1] <= self.save_y + self.save_label.get_height():
                    print("save")
                    lvl_number = 0
                    while True:
                        try:
                            with open(f"levels/level_{lvl_number}.txt", "rb") as f:
                                lvl_number += 1
                        except FileNotFoundError:
                            break
                    save_level(lvl_number, self.grid, self.game_objects)

                # click on load
                if self.load_x <= event.pos[0] <= self.load_x + self.load_label.get_width() \
                        and self.load_y <= event.pos[1] <= self.load_y + self.load_label.get_height():
                    print("load")

                    file = ask_file()

                    if file == "":
                        return
                    self.grid, self.game_objects = load_level_2(file)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.dragging:
                    s_width, s_height = pygame.display.get_surface().get_size()
                    w, h = 500, 500
                    x0 = (s_width - w) // 2
                    y0 = (s_height - h) // 2
                    i = (event.pos[1] - y0) * self.grid.n // h
                    j = (event.pos[0] - x0) * self.grid.m // w
                    id_color = -1
                    for obj in self.game_objects:
                        if obj.type == "laser_door":
                            id_color = max(id_color, obj.id_color)
                    id_color += 1

                    p_i, p_j = self.drag_start

                    if p_i == i:
                        is_vertical = False
                        start = i, min(p_j, j)
                        end = i, max(p_j, j)
                    else:
                        is_vertical = True
                        start = min(p_i, i), j
                        end = max(p_i, i), j
                    self.game_objects.append(LaserDoor(start, end, self.grid, is_vertical, id_color))
                    self.dragging = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP_PLUS:
                    self.grid.add_row()
                    self.grid.add_column()
                if event.key == pygame.K_KP_MINUS:
                    self.grid.remove_row()
                    self.grid.remove_column()

    def draw(self, win):
        s_width, s_height = pygame.display.get_surface().get_size()
        w, h = 500, 500
        x0 = (s_width - w) // 2
        y0 = (s_height - h) // 2
        self.grid.draw(win, (x0, y0, w, h), draw_grid=True)

        for obj in self.game_objects:
            obj.draw(win, x0, y0, w, h)
        # draw erase button
        win.blit(self.erase_label, (self.erase_x, self.erase_y))

        # draw save button
        win.blit(self.save_label, (self.save_x, self.save_y))

        # draw load button
        win.blit(self.load_label, (self.load_x, self.load_y))
        pygame.display.update()


def ask_file():
    top = tkinter.Tk()
    top.withdraw()
    file = tkinter.filedialog.askopenfilename(initialdir="levels", title="Select file",
                                              filetypes=(("text files", "*.txt"), ("all files", "*.*")))
    top.destroy()
    return file



def save_level(level_number, grid: Grid, game_objects: list):
    with open(f"levels/level_{level_number}.txt", "w") as f:
        f.write(f"{grid.n} {grid.m}\n")
        for i in range(grid.n):
            for j in range(grid.m):
                f.write(f"{grid.grid[i][j]}")
        f.write("\n")
        for obj in game_objects:
            f.write(obj.type + "\n")
            if obj.type == "button":
                f.write(f"{obj.i} {obj.j} {obj.id_color}\n")
            elif obj.type == "laser_door":
                print(obj.Isvertical)
                f.write(
                    f"{obj.start_pos[0]} {obj.start_pos[1]} {obj.end_pos[0]} {obj.end_pos[1]} {obj.Isvertical} {obj.id_color}\n")
            else:
                raise ValueError(f"Unknown type {obj.type}")


def load_level_2(path) -> (Grid, list):
    with open(path, "r") as f:
        n, m = f.readline().split()
        grid = Grid(int(n), int(m))
        for i in range(grid.n):
            for j in range(grid.m):
                grid.grid[i][j] = int(f.read(1))
        f.readline()
        game_objects = []
        for line in f:
            line = line.strip()
            if line == "button":
                i, j, id_color = f.readline().split()
                game_objects.append(Button(int(i), int(j), grid, int(id_color)))
            elif line == "laser_door":
                i, j, i2, j2, Isvertical, id_color = f.readline().split()
                game_objects.append(
                    LaserDoor((int(i), int(j)), (int(i2), int(j2)), grid, Isvertical == "True", int(id_color)))
            else:
                raise ValueError(f"Unknown type {line}")

    return grid, game_objects



class