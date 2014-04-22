#!/usr/bin/python
# -*- coding: utf-8 -*-


class RegnancyException(Exception):

    """base class for exceptions in Regnancy"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class CardNotInHandException(RegnancyException):

    """The card can not be accessed, due it is not in the hand of the player"""

    pass


class PileIsEmptyException(RegnancyException):

    """An Operation on a pile could not be fullfiled, due it is empty"""

    pass


class NotEnoughMoneyException(RegnancyException):

    """Could not buy a card, due the player has not enough money"""

    pass


class CardToExpensiveToPickException(RegnancyException):

    """Could not pick a card, due the card is to expensive"""

    pass


