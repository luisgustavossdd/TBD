#!/usr/bin/python
# -*- coding: utf-8 -*-

import copy
from framework.misc import get_id

ACTION = 0x0001
ATTACK = 0x0002
TREASURE = 0x0004
CURSE = 0x0008
REACTION = 0x0010
DURATION = 0x0020
VICTORY = 0x0040


class Card(object):

    """Represents a Card"""

    def __init__(self):
        self.id = get_id()
        self.virtual = False

    def copy(self):
        copied_card = copy.copy(self)
        copied_card.id = get_id()
        copied_card.virtual = True
        return copied_card

    def gain_step(self, game, player):
        """Defines what happens when the player gains this card"""

        pass

    def begin_step(self, game, player):
        """Defines what happens when this card is in play at the beginning of the turn (Duration Cards)"""

        pass

    def action_step(self, game, player):
        """Defines what happens when this card is played in the action step"""

        pass

    def buy_step(self, game, player):
        """Defines what happens when this card is played in the buy step"""

        pass

    def end_step(self, game, player):
        """Defines what happens when this card is in the deck at the end of the game"""

        pass

    def cleanup_step(self, game, player):
        """Defines what happens when this card is in player in the (pre-) clean up step"""

        pass

    def handler(self, game, player, result):
        raise Exception('This handler is supposed to be overriden')

    def handle_trigger(self, trigger):
        pass

#     def getMoney(self):
#         return (0,0)
#     
#     @staticmethod
#     def getVictoryPoints():
#         return 0
#     
#     @staticmethod
#     def getBonusBuys():
#         return 0
#     
#     @staticmethod
#     def getBonusCards():
#         return 0
    
    money = (0,0)
    victoryPoints = 0
    extra_actions= 0
    extra_cards= 0
    extra_buys= 0
    known = False
    
    @classmethod
    def getInstructions(cls):
        return cls.instructions

    @classmethod
    def getMoney(cls):
        return cls.money
    
    @classmethod
    def getVictoryPoints(cls):
        return cls.victoryPoints
    
    @classmethod
    def getBonus(cls):
        return (cls.extra_actions,cls.extra_cards,cls.extra_buys)
    
    @classmethod
    def getBonusActions(cls):
        return cls.extra_actions
     
    @classmethod
    def getBonusCards(cls):
        return cls.extra_cards
     
    @classmethod
    def getBonusBuys(cls):
        return cls.extra_buys
     
    @classmethod
    def knowHowUse(cls):
        return cls.known