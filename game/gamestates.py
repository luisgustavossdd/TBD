#!/usr/bin/python
# -*- coding: utf-8 -*-

P_ACTION = "action"
P_BUY = "buy"
P_PRECLEANUP = "precleanup"
P_CLEANUP = "cleanup"
P_END = "end"  # the game is over

SP_PLAYERINPUT = 'playerinput'  # the player has to choose to play/buy a card
SP_PICKCARD = 'pickcard'  # player has to pick a card from any pile
SP_PICKCARDSFROMHAND = 'pickcardsfromhand'  # player has to pick a card from hand
SP_ORDERCARDS = 'ordercards' # let the player order some cards, e.g. Scout/Secret Chamber
SP_ASKPLAYER = 'answer'  # ask the player for input
SP_WAIT = 'wait'

CANCEL_ATTACK = 'cancel'