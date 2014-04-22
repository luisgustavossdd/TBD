#!/usr/bin/python
# -*- coding: utf-8 -*-

from askplayerinfo import AskYesNo, CardAskPlayerInfo
from gamestates import SP_ASKPLAYER
from infotoken import InfoToken


class SubPhaseInfo(object):

    def __init__(self, subphase, card=None, info=None, callback=None,
                 on_restore_callback=None):

        assert subphase
        if info:
            assert isinstance(info, InfoToken)
        
        self.card = card
        self.subphase = subphase
        self.info = info
        self.callback = callback
        self.on_restore_callback = on_restore_callback


class AskSubPhase(SubPhaseInfo):

    def __init__(self, card, text, answers, callback,
                 on_restore_callback=None, card_to_show=None):
        SubPhaseInfo.__init__(self, SP_ASKPLAYER, card,
                              CardAskPlayerInfo(card, text, answers,
                              card_to_show), callback,
                              on_restore_callback)


class YesNoSubPhase(SubPhaseInfo):

    def __init__(self, card, text, callback, on_restore_callback=None,
                 card_to_show=None):
        SubPhaseInfo.__init__(self, SP_ASKPLAYER, card_to_show or card,
                              AskYesNo(card, text, card_to_show),
                              callback, on_restore_callback)


