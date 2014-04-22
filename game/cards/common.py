#!/usr/bin/python
# -*- coding: utf-8 -*-

from game.cards.card import Card, TREASURE, VICTORY, CURSE


class Silver(Card):

    cardtype = TREASURE
    cost = (3, 0)
    name = 'Silver'

    def __init__(self):
        Card.__init__(self)

    def buy_step(self, game, player):
        player.money += 2
    
    def action_step(self, game, player):
        self.buy_step(game, player)


class Curse(Card):

    cardtype = CURSE
    cost = (0, 0)
    name = 'Curse'

    def __init__(self):
        Card.__init__(self)

    def end_step(self, game, player):
        player.score -= 1


class Estate(Card):

    cardtype = VICTORY
    cost = (2, 0)
    name = 'Estate'

    def __init__(self):
        Card.__init__(self)

    def end_step(self, game, player):
        player.score += 1


class Potion(Card):

    cardtype = TREASURE
    cost = (4, 0)
    name = 'Potion'

    def __init__(self):
        Card.__init__(self)

    def buy_step(self, game, player):
        player.potion += 1

    def action_step(self, game, player):
        self.buy_step(game, player)


class Duchy(Card):

    cardtype = VICTORY
    cost = (5, 0)
    name = 'Duchy'

    def __init__(self):
        Card.__init__(self)

    def end_step(self, game, player):
        player.score += 3


class Copper(Card):

    cardtype = TREASURE
    cost = (0, 0)
    name = 'Copper'

    def __init__(self):
        Card.__init__(self)

    def buy_step(self, game, player):
        player.money += 1

    def action_step(self, game, player):
        self.buy_step(game, player)


class Province(Card):

    cardtype = VICTORY
    cost = (8, 0)
    name = 'Province'

    def __init__(self):
        Card.__init__(self)

    def end_step(self, game, player):
        player.score += 6


class Gold(Card):

    cardtype = TREASURE
    cost = (6, 0)
    name = 'Gold'

    def __init__(self):
        Card.__init__(self)

    def buy_step(self, game, player):
        player.money += 3

    def action_step(self, game, player):
        self.buy_step(game, player)


