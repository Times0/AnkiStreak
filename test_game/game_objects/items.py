from objects import GameObject_no_pos


class Item(GameObject_no_pos):
    def __init__(self, name, img, size=(50, 50)):
        super().__init__(size, img)
        self.name = name

    def draw(self, win):
        win.blit(self.zoom_buffer, self.rect)
