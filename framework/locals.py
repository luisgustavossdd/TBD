#!/usr/bin/python
# -*- coding: utf-8 -*-

ACTION = 'action'  # Invoke a specific action

INITIAL = 'initial'  # tell the client to initialize, since it is successfully connected. Needs ID.
SETMASTER = 'setmaster'  # set the clients mastermode, usually the creator of the game. Needs a boolean VALUE.
MESSAGE = 'message'

UPDATE = 'update'
END = 'end'
START = 'start'

PLAYERINFO = 'update_PLAYERINFO'
HAND = 'update_HAND'
BOARD = 'update_BOARD'
BOARDSETUP = 'update_BOARDSETUP'
BOARDCOMMON = 'update_BOARDCOMMON'
NEWCARD = 'update_NEWCARD'
PHASE = 'update_PHASE'
CLIENTID = 'update_CLIENTID'
SUBPHASE = 'update_SUBPHASE'
DECK = 'update_DECK'

CHANGENAME = 'changename'  # tell the server about the new name of a client. Needs the new name in VALUE.
REQUEST = 'request'  # reguest a new game-action. Needs the type of request in VALUE.
RESPONSE = 'response'  # a game action, can be one of the following three:

BUYFROMPILE = 'response_BUYFROMPILE'
PLAYCARD = 'response_PLAYCARD'
ANSWER = 'response_ANSWER'

GAMESTART = 'gamestart'  # tell the server to start the game
ENDPHASE = 'endphase'  # tell the server the player wants to end the current phase

MESSAGE = 'message'  # contains a message-string.
ID = 'id'  # contains an ID, usually the sending client.
SUBID = 'subid' # contains an ID, usually the card that was played
MENU = "menu"

VALUE = "value"
INFO = "info"
RESULT = "result"

BLUE = (10, 10, 240)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
