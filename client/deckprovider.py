#!/usr/bin/python
# -*- coding: utf-8 -*-

from framework.configprovider import ConfigProvider
import os

__config_provider = ConfigProvider()


def get_all_deck_names():
    return [f for f in __config_provider.get_files('decks') if f.endswith('.deck')]


def save_deck(deck_name, card_name_list):
    __config_provider.write(os.path.join('decks', deck_name + '.deck'),
                            ("\n").join(card_name_list))


def load_deck(deck_name):
    return [c.replace("\n", '') for c in __config_provider.read(os.path.join('decks',
            deck_name + '.deck'))]


