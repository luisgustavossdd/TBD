#!/usr/bin/python
# -*- coding: utf-8 -*-

import cards

def get_all_card_classes():
    return cards.card.Card.__subclasses__()[:]  #@UndefinedVariable
