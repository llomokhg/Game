import pygame


class Button:
    def __init__(self, pos, size, normal_color, holding_color, text_color, font, font_size, text):
        self.pos = pos
        self.size = size
        self.normal_color = normal_color
        self.holding_color = holding_color
        self.text_color = text_color
        self.color = self.normal_color
        self.font = font
        self.font_size = font_size
        self.text = text

    def holding(self, pos):
        if self.click_checking(pos):
            self.color = self.holding_color
        else:
            self.color = self.normal_color

    def drawing(self, window):
        pygame.draw.rect(window, self.color, (self.pos[0] - (self.size[0] // 14), self.pos[1],
                                              *self.size), border_radius=10)
        window.blit(pygame.font.SysFont(self.font, self.font_size).render(self.text, False, self.text_color),
                    self.pos)

    def click_checking(self, pos):
        if self.pos[0] <= pos[0] <= self.pos[0] + self.size[0] and self.pos[1] <= pos[1] <= self.pos[1] + self.size[1]:
            return True
