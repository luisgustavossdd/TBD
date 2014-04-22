#!/usr/bin/python
# -*- coding: utf-8 -*-

from random import shuffle
from uuid import uuid4

from framework.regnancyexception import PileIsEmptyException
from cards.card import ACTION, TREASURE, VICTORY


class Pile(object):

    """Represents a pile of cards."""

    def __init__(self):
        self.cards = []
        self.id = uuid4()

    def __getitem__(self, key):
        return (self.cards)[key]

    def add(self, card):
        """Puts a card on top of the pile"""

        if not card in self.cards:
            self.cards.append(card)

    def remove(self, card):
        """Removes a card from the pile"""

        self.cards.remove(card)

    def take(self, save=False):
        """Returns the top card of the pile"""

        try:
            return self.cards.pop()
        except:
            if save:
                return None
            raise PileIsEmptyException("Can't take next card")

    def shuffle_into(self, other_pile):
        """Shuffles all cards in this pile into the other pile"""

        other_pile.cards.extend(self.cards)
        other_pile.shuffle()
        self.cards = []

    def shuffle(self):
        """Shuffles the pile"""

        shuffle(self.cards)

    @property
    def bottom_card(self):
        return (self.cards)[0]

    def __len__(self):
        """Returns the number of cards in the pile"""

        return len(self.cards)

    def __iter__(self):
        """Returns the piles iteration-object"""

        return self.forward()

    def forward(self):
        """Returns the forward-generator"""

        current_item = 0
        while current_item < len(self.cards):
            card = (self.cards)[current_item]
            current_item += 1
            yield card

    def sort(self, **kwargs):
        self.cards.sort(**kwargs)

    def reverse(self):
        """Returns the backward-generator"""

        current_item = len(self.cards)
        while current_item > 0:
            current_item -= 1
            yield (self.cards)[current_item]

    def get_card(self, card_id):
        """Returns the cards with the given card id"""

        return next(c for c in self if c.id == card_id)

    def get_actions(self):
        """Returns all action cards from this pile"""

        return self.get_all_of_card_type(ACTION)

    def get_treasures(self):
        """Returns all treasure cards from this pile"""

        return self.get_all_of_card_type(TREASURE)

    def get_victories(self):
        """Returns all victory cards from this pile"""

        return self.get_all_of_card_type(VICTORY)

    def get_all_of_card_type(self, card_type):
        return [c for c in self if c.cardtype & card_type]

    def get_all_of_card_class(self, card_class):
        """ Returns all cards of a given class, e.g. Duchy or Copper"""

        return [c for c in self if isinstance(c, card_class)]


class KingdomPile(Pile):

    """Represents a pile of kingdom cards."""

    def __init__(self, cardtype, count):
        Pile.__init__(self)
        self.name = cardtype.name
        self.cost = cardtype.cost
        self.card = cardtype
        self.initialsize = count
        for _ in xrange(count):
            self.cards.append(cardtype())


