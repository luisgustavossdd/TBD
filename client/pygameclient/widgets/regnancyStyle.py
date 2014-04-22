#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygame
import os

fullname = os.path.join('res', 'gui')


def init(gui):

    buttonsurf = pygame.image.load(os.path.join(fullname, 'button.png')).convert_alpha()
    closesurf = pygame.image.load(os.path.join(fullname,
                                  'closebutton.png')).convert_alpha()
    shadesurf = pygame.image.load(os.path.join(fullname,
                                  'shadebutton.png')).convert_alpha()
    checksurf = pygame.image.load(os.path.join(fullname, 'checkbox.png')).convert_alpha()
    optionsurf = pygame.image.load(os.path.join(fullname,
                                   'optionbox.png')).convert_alpha()
    combosurf = pygame.image.load(os.path.join(fullname, 'combobox.png')).convert_alpha()

    gui.defaultFont = pygame.font.Font(os.path.join('res/fonts',
            'font.ttf'), 19)

    gui.defaultLabelStyle = {'font-color': (255, 255, 255), 'font': gui.defaultFont,
                             'autosize': True, "antialias": True,
                             'border-width': 0, 'border-color': (255,
                             255, 255), 'wordwrap': False}

    gui.defaultButtonStyle = gui.createButtonStyle(
        gui.defaultFont,
        (0, 0, 0),
        buttonsurf,
        4,
        1,
        4,
        4,
        1,
        4,
        4,
        1,
        4,
        4,
        1,
        4,
        )

    closeButtonStyle = gui.createImageButtonStyle(closesurf, 20)

    shadeButtonStyle = gui.createImageButtonStyle(shadesurf, 20)

    gui.defaultWindowStyle = {
        'font': gui.defaultFont,
        'font-color': (255, 255, 255),
        'bg-color': (0, 0, 0, 150),
        'shaded-bg-color': (0, 50, 100, 100),
        'shaded-font-color': (255, 200, 0),
        'border-width': 1,
        'border-color': (150, 150, 150, 255),
        'offset': (5, 5),
        'close-button-style': closeButtonStyle,
        'shade-button-style': shadeButtonStyle,
        }

    gui.defaultTextBoxStyle = {
        'font': gui.defaultFont,
        'font-color': (255, 255, 255),
        'bg-color-normal': (55, 55, 55),
        'bg-color-focus': (70, 70, 80),
        'border-color-normal': (0, 0, 0),
        'border-color-focus': (0, 50, 50),
        'border-width': 1,
        'appearence': gui.APP_3D,
        "antialias": True,
        'offset': (4, 4),
        }

    gui.defaultCheckBoxStyle = gui.createCheckBoxStyle(gui.defaultFont,
            checksurf, 12, (255, 255, 255), (100, 100, 100), autosize=
            True)

    gui.defaultOptionBoxStyle = gui.createOptionBoxStyle(gui.defaultFont,
            optionsurf, 12, (255, 255, 255), (100, 100, 100), autosize=
            True)

    gui.defaultListBoxStyle = {
        'font': gui.defaultFont,
        'font-color': (255, 255, 255),
        'font-color-selected': (0, 0, 0),
        'bg-color': (55, 55, 55),
        'bg-color-selected': (160, 180, 200),
        'bg-color-over': (60, 70, 80),
        'border-width': 1,
        'border-color': (0, 0, 0),
        'item-height': 22,
        'padding': 2,
        'autosize': False,
        }

    gui.defaultComboBoxStyle = gui.createComboBoxStyle(gui.defaultFont,
            combosurf, 15, (255, 255, 255), borderwidth=1, bordercolor=(31,
            52, 78), bgcolor=(55, 55, 55))


