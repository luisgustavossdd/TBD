#!/usr/bin/python
# -*- coding: utf-8 -*-

from framework.regnancyexception import *
from pile import Pile
from playerinfo import PlayerInfo
from cards.card import ACTION


class Player(object):

    """This class represents a player that plays the game."""

    def __init__(self, name, game, id):
        self.name = name
        self.id = id
        self.actions = 0
        self.buys = 0
        self.money = 0
        self.score = 0
        self.potion = 0
        self.game = game
        self.hand = Pile()
        self.board = Pile()
        self.deck = Pile()
        self.durations = Pile()
        self.drawpile = Pile()
        self.discardpile = Pile()

    def move_card_to_pile(self, card, target_pile):
        """Moves a card from the draw pile, the discard pile, or the hand to another target pile"""

        for p in (self.drawpile, self.discardpile, self.hand):
            if card in p:
                p.remove(card)
        target_pile.add(card)

    def create_info(self):
        """Creates an PlayerInfo-Object containing public informations about this player"""

        return PlayerInfo(
            self.name,
            len(self.hand),
            len(self.drawpile),
            len(self.discardpile),
            self.actions,
            self.buys,
            self.money,
            self == self.game.active_player,
            self.score,
            self.potion,
            self.id,
            )

    def can_do_action(self):
        """Indicates if the player can play an action card"""

        return self.actions > 0 and len([c for c in self.hand if c.cardtype &
                ACTION]) > 0

    def play_card(self, card_id):
        """Play the given card"""

        card = [card for card in self.hand if card.id == card_id]
        if not card:
            raise CardNotInHandException("Can't play %s" % card_id)
        card = card[0]
        self.hand.remove(card)
        self.board.add(card)

    def discard_card(self, card):
        """Discards the given card from the hand"""

        if not card in self.hand:
            raise CardNotInHandException("Can't discard %s" % card)
        self.hand.remove(card)
        self.discardpile.add(card)

    def put_on_drawpile(self, card):
        if card:
            self.deck.add(card)
            self.drawpile.add(card)

    def trash_card(self, card):
        """Remove a card from the deck and put it onto the games trashpile"""

        try:
            self.deck.remove(card)
        except ValueError:
            pass
        try:
            self.board.remove(card)
        except ValueError:
            pass
        try:
            self.hand.remove(card)
        except ValueError:
            pass
        try:
            self.discardpile.remove(card)
        except ValueError:
            pass
        try:
            self.durations.remove(card)
        except ValueError:
            pass

    def take_card(self, card, to_hand=False, to_deck=False):
        """Take a card and put in into the discard pile or hand or deck"""

        self.deck.add(card)

        if to_hand:
            self.hand.add(card)
        elif to_deck:
            self.drawpile.add(card)
        else:
            self.discardpile.add(card)

    def draw_card(self, just_reveal=False):
        """Draw a card. If the drawpile is empty, shuffle the discardpile into
    the drawpile and try again. If the drawpile is still empty, do nothing"""

        card = None
        try:
            card = self.drawpile.take()
        except PileIsEmptyException:
            self.discardpile.shuffle_into(self.drawpile)
            try:
                card = self.drawpile.take()
            except PileIsEmptyException:
                pass

        if card and not just_reveal:
            self.hand.add(card)
        return card


