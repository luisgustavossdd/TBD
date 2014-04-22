#!/usr/bin/python
# -*- coding: utf-8 -*-


class StepHandler(object):
    """
    A StepHandler takes a card class (e.g. Copper or Transmute) and a
    callback f(game, player). When the StepHandler is called, it
    checks if the card passed is an instance of the card class given
    and if so, calls the given callback""" 
    

    def __init__(self, card_class, callback):
        assert card_class
        assert callback
        self.card_class = card_class
        self.callback = callback

    def __call__(self, game, player, card):
        if isinstance(card, self.card_class):
            self.callback(game, player)


