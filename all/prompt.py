import pygame


class Window:
    def __init__(self, pos, square_size, huge_text, all_text, layer):
        self.pos = pos
        self.grab = False
        self.width, self.height = square_size
        self.grab_pos = (0, 0)
        self.exist = True
        self.layer = layer
        self.huge_text = huge_text
        self.all_text = all_text
        self.huge_font = pygame.font.SysFont('Comic Sans MS', 30)
        self.font = pygame.font.SysFont('Comic Sans MS', 15)

    def draw(self, window):
        count = 1
        pygame.draw.rect(window, (50, 50, 50), (self.pos[0], self.pos[1], self.width, self.height), border_radius=20)
        pygame.draw.rect(window, (0, 0, 0), (self.pos[0], self.pos[1], self.width, self.height // 20), border_radius=10)
        pygame.draw.rect(window, (0, 0, 0), (self.pos[0], self.pos[1], self.width, self.height), 5, 20)
        pygame.draw.rect(window, (255, 0, 0), (self.pos[0] + self.width - self.height // 10,
                                               self.pos[1], self.height // 10, self.height // 10),
                         border_radius=7)
        window.blit(self.huge_font.render(self.huge_text, False, (255, 0, 255)), (self.pos[0] + self.width // 10,
                                                                                  self.pos[1] +
                                                                                  self.height // 10))
        if type(self.all_text) == list:
            for text in self.all_text:
                if self.layer == 'areas' or self.layer == 'area_select':
                    text = text.get_class()
                window.blit(self.font.render(text, False, (255, 0, 255)), (self.pos[0] + self.width // 10,
                                                                           self.pos[1] +
                                                                           (self.height // 20) * count +
                                                                           self.height // 5))
                count += 1
        else:
            window.blit(self.font.render(self.all_text, False, (255, 0, 255)), (self.pos[0] + self.width // 10,
                                                                                self.pos[1] +
                                                                                (self.height // 20) * count +
                                                                                self.height // 5))

    def grabbing(self, pos):
        if self.grab_pos[1] <= self.height // 10 and self.grab:
            self.pos = (pos[0] - self.grab_pos[0], pos[1] - self.grab_pos[1])

    def grabbed(self, pos):
        if self.pos[0] <= pos[0] <= self.pos[0] + self.width and \
                self.pos[1] <= pos[1] <= self.pos[1] + self.height:
            return True

    def begin_grabbing(self, pos):
        if self.pos[0] + self.width - self.height // 6 <= pos[0] <= self.pos[0] + self.width and \
                self.pos[1] <= pos[1] <= self.pos[1] + self.height // 6:
            self.exist = False
        else:
            self.grab = True
            self.grab_pos = pos
            self.grab_pos = (self.grab_pos[0] - self.pos[0], self.grab_pos[1] - self.pos[1])
