#!/usr/bin/python
# -*- coding: utf-8 -*-

from infotoken import InfoToken

class AskPlayerInfo(InfoToken):

    def __init__(self, title, text, answers, card_to_show=None):
        InfoToken.__init__(self, text)
        
        assert title
        assert answers
        self.title = title
        self.answers = answers
        
        try:
            self.card_to_show = card_to_show.name
        except AttributeError:
            self.card_to_show = card_to_show


class CardAskPlayerInfo(AskPlayerInfo):

    def __init__(self, card, text, answers, card_to_show=None):
        AskPlayerInfo.__init__(self, card.__class__.name, text, answers,
                               card_to_show or card)


class AskYesNo(CardAskPlayerInfo):

    def __init__(self, card, text, card_to_show=None):
        CardAskPlayerInfo.__init__(self, card, text, ('Yes', 'No'),
                                   card_to_show)


