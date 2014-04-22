#!/usr/bin/python
# -*- coding: utf-8 -*-

from client.pygameclient.settings import *
import pygame


def full_to_prev(card):
    final = pygame.Surface((PREV_WIDTH, PREV_HEIGHT))
    SC_H = int((CARD_HEIGHT * PREV_WIDTH) / CARD_WIDTH)
    sc = pygame.transform.smoothscale(card, (PREV_WIDTH, SC_H))

    rt = pygame.Rect(0, 0, PREV_WIDTH, SC_H / 1.847)
    top = sc.subsurface(rt)

    bp = SC_H / 8
    rb = pygame.Rect(0, SC_H - bp, PREV_WIDTH, bp)
    bot = sc.subsurface(rb)

    final.blit(top, (0, 0))
    final.blit(bot, (0, SC_H / 1.847))
    return final


def full_to_small(card):
    final = pygame.Surface((SMALL_WIDTH, SMALL_HEIGHT))
    SC_H = (CARD_HEIGHT * SMALL_WIDTH) / CARD_WIDTH
    sc = pygame.transform.smoothscale(card, (SMALL_WIDTH, SC_H))

    cut = 7.9

    rt = pygame.Rect(0, 0, SMALL_WIDTH, SC_H / cut)
    top = sc.subsurface(rt)

    bp = SC_H / 8
    rb = pygame.Rect(0, SC_H - bp, SMALL_WIDTH, bp)
    bot = sc.subsurface(rb)

    final.blit(top, (0, 0))
    final.blit(bot, (0, SC_H / cut))
    return final


