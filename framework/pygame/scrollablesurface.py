#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygame

RECT_SIZE = 20


class ScrollableSurface(pygame.Surface):

    def __init__(self, size, pos, scroll_speed=7):
        pygame.Surface.__init__(self, size)

        self.x_offset = 0
        self.y_offset = 0

        self.pos = pos

        self.scroll_speed = scroll_speed

        self.upper_rect = pygame.Rect(0, 0, size[0], RECT_SIZE)
        self.lower_rect = pygame.Rect(0, size[1] - RECT_SIZE, size[0],
                RECT_SIZE)
        self.left_rect = pygame.Rect(0, 0, RECT_SIZE, size[1])
        self.right_rect = pygame.Rect(size[0] - RECT_SIZE, 0, RECT_SIZE,
                size[1])

    def draw(self, surface, sub_surface):
        (x, y) = self.pos
        self.fill((0, 0, 0))
        (mx, my) = pygame.mouse.get_pos()

        max_x_offset = sub_surface.get_width() - self.get_width()

        if self.left_rect.collidepoint((mx - x, my - y)) and self.x_offset != \
            0:
            self.x_offset += self.scroll_speed

        if self.x_offset > 0:
            self.x_offset = 0

        if self.right_rect.collidepoint((mx - x, my - y)) and -self.x_offset < \
            max_x_offset:
            self.x_offset -= self.scroll_speed

        if -self.x_offset > max_x_offset and self.x_offset < 0:
            self.x_offset = -max_x_offset

        self.blit(sub_surface, (self.x_offset, self.y_offset))

        def blit(rect):
            self.fill((200, 0, 0), rect=rect, special_flags=pygame.BLEND_RGBA_MULT)

        if self.x_offset < 0:
            blit(self.left_rect)

        if sub_surface.get_width() > self.get_width() - self.x_offset:
            blit(self.right_rect)

        surface.blit(self, (x, y))


