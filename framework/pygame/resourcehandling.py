#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygame
import logging

def load_image(filename, size=False):
    """Loads an image into a pygame Surface-object"""

    try:
        image = pygame.image.load(filename)
        
        if size:
            image = scale_image(image, (int(size[0]), int(size[1])))
        return image.convert_alpha()  #Convert any transparency in the image
    except:
        logging.error('Unable to load: %s', filename)


def load_font(filename, size):
    """Loads a font into a pygame Font-object"""

    try:
        return pygame.font.Font(filename, 160)
    except:
        logging.error('Unable to load font: %s', filename)


def load_sound(filename):
    """Loads a sound into a pygame Sound-object"""

    try:
        return pygame.mixer.Sound(filename)
    except:
        logging.error('Unable to load sound: %s', filename)


def scale_image(image, size):
    """scales a pygame Surface to the given size"""

    return pygame.transform.smoothscale(image, size)

default_image = None
def get_default_image(*args):
    global default_image
    if not default_image:
        default_image = pygame.Surface((50, 50))
        default_image.fill((255, 0, 0))
        f = pygame.font.SysFont('default', 20).render("ERR", True, (255, 255, 255))
        default_image.blit(f, (0 ,0))
    return lambda *args: default_image

class LazyImageLoader(object):
    def __init__(self, filename, modifier, size):
        self.images = {}
        self.filename = filename
        self.modifier = modifier
        self.size = size

    def load(self):
        image = load_image(self.filename, self.size)
         
        self.images[None] = image
        self.images[()] = image
        self.images[''] = image
        
        if self.modifier:
            for suffix in self.modifier:
                self.images[suffix] = self.modifier[suffix](image) 
            
    def __call__(self, suffix):
        if not self.images:
            self.load()
        return self.images[suffix]

def blurSurf(surface, amt):
    scale = 1.0 / float(amt)
    surf_size = surface.get_size()
    scale_size = (int(surf_size[0] * scale), int(surf_size[1] * scale))
    surf = pygame.transform.smoothscale(surface, scale_size)
    surf = pygame.transform.smoothscale(surf, surf_size)
    return surf


class Fontrenderer(object):

    def __init__(self):
        self.s_c = {}
        self.c = {}

    def render(self, font, text, color, surf, pos):

        if not (font, text, str(color)) in self.s_c.keys():
            (self.s_c)[(font, text, str(color))] = blurSurf(font.render(text.decode('utf-8'),
                    True, (0, 0, 0)), 1.6)

        ss = (self.s_c)[(font, text, str(color))]
        surf.blit(ss, (pos[0] + 1, pos[1] + 2))

        if not (font, text, str(color)) in self.c.keys():
            (self.c)[(font, text, str(color))] = font.render(text.decode('utf-8'),
                    True, color)

        s = (self.c)[(font, text, str(color))]
        surf.blit(s, pos)