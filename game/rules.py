#!/usr/bin/python
# -*- coding: utf-8 -*-

import random


from client import deckprovider
import cardprovider
from cards.common import Copper, Duchy, Estate, Gold, Potion, Province, \
    Silver, Curse
from cards.card import VICTORY, CURSE
from cards.base import Village, Moat, Militia, Witch, Workshop
from cards.promo import WalledVillage
from cards.seaside import Treasury, Warehouse
from cards.cornucopia import BagOfGold, Diadem, Followers, Princess, \
    TrustySteed
from cards.hinterlands import Embassy, Oasis, IllGottenGains, FoolsGold,\
    Crossroads
from cards.intrigue import Torturer, SecretChamber, Swindler, WishingWell,\
    Saboteur, Scout, Nobles, Harem
from cards.alchemy import Apothecary, Herbalist, ScryingPool, Alchemist,\
    Philosophersstone
import global_options
from cards.prosperity import Bank, CountingHouse
from pile import KingdomPile
from cards.intrigue import Minion

commonpiles = (Copper, Silver, Gold, Potion, Estate, Duchy, Province,
               Curse)

def prepare_piles(list_of_cards, num_players):
    """set up the piles, e.g. 10 each Action-Card, 12 or 8 of each Treasure etc."""

    piles = []
    for card in list_of_cards:
        if card in (Gold, Silver, Copper, Potion):
            count = 99
        elif card.cardtype == VICTORY:
            if global_options.debug_mode and 0:
                count = 3
            else:
                count = 12 if num_players > 2 else 8
        elif card.cardtype == CURSE:
            count = (num_players - 1) * 10
        else:
            count = 10
        piles.append(KingdomPile(card, count))
    return piles


def standarddeck():
    deck = []

    if global_options.debug_mode:
        [deck.append(Copper()) for _ in xrange(7)]
        [deck.append(Minion()) for _ in xrange(3)]
        [deck.append(Militia()) for _ in xrange(3)]
    else:
        [deck.append(Copper()) for _ in xrange(7)]
        [deck.append(Estate()) for _ in xrange(3)]
    random.shuffle(deck)
    return deck


def randomsetup():

    def card_filter(c):
        return not c in commonpiles and not c in [BagOfGold, Diadem,
                Followers, Princess, TrustySteed]

    cards = [c for c in cardprovider.get_all_card_classes() if card_filter(c)]
    random.shuffle(cards)
    if global_options.debug_mode:
        d =[]# [IllGottenGains, FoolsGold]
        d.extend(cards[:10-len(d)])
        return d
    else:
        return cards[:10]


def get_setup(setup):
    if setup == 'random':
        return randomsetup()
    else:
        deck = deckprovider.load_deck(setup)
        return [c for c in cardprovider.get_all_card_classes() if c.name in deck]


def game_end(game):
    p = len(game.get_pile(Province))
    e = len([pile for pile in game.allpiles if not len(pile)])
    return p == 0 or e >= 3