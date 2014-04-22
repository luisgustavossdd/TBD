#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
from itertools import chain

from framework.event import *
from game.gamestates import SP_PLAYERINPUT, P_BUY, P_ACTION,\
    SP_PICKCARDSFROMHAND, SP_ASKPLAYER
##from game.cards.common import Province, Gold, Silver
from game.cards.common import *
from game.cards.base import *
from game.cards.intrigue import *

from framework.async import PP_QUIT, get_timeout_pipe
from framework.networking import find_server
import logging
import random
from game.cards.card import ACTION, TREASURE

names = [
    'Jacob',
    'Isabella',
    'Ethan',
    'Emma',
    'Michael',
    'Olivia',
    'Alexander',
    'Sophia',
    'William',
    'Ava',
    'Joshua',
    'Emily',
    'Daniel',
    'Madison',
    'Jayden',
    'Abigail',
    'Noah',
    'Chloe',
    'Anthony',
    'Mia',
    ]


def get_random_name():
    return random.choice(names)

def get_aiclient(pipe):
    return _AiClient(pipe, _BigMoneyStrategy())

def _crap_generator(aiclient):
    for c in (c for c in aiclient.hand if c.name in ("Duchy", "Province", "Estate")):
        yield c
    actions = [c for c in aiclient.hand if c.cardtype & ACTION] 
    if len(actions) > 3:
        for c in actions[:2]:
            yield c
    for c in aiclient.hand:
        yield c


def can_afford(aiclient, card):
    return aiclient.player.money >= card.cost[0] and aiclient.player.potion >= card.cost[1]  

def count(aiclient, card):
    return len([c for c in aiclient.deck if isinstance(c, card)])

class _Strategy(object):
    
    def _cards_to_buy_gen(self, aiclient):
        for c in Province, Gold, Silver:
            yield c
    
    def choose_card_to_buy(self, aiclient):
        gen = self._cards_to_buy_gen(aiclient)
        return next((c for c in gen if can_afford(aiclient, c)), None)
    
    def handle_card(self, aiclient, card):
##        print ">>>>>>>>>>>>>>>>>>>>>>>>>>Need to answeerr!!"
##        logging.debug("%s",[step for step in dir(card) if "_step" in step])
        
        handler = getattr(self, '_handle_card_' + card.name.lower())
        if handler not in dir(self): return
        handler(aiclient, card)
        
    def _handle_card_militia(self, aiclient, card):
        num_hand = len(aiclient.hand)
        aiclient.discard_crap(num_hand - 3)
    
    def _handle_card_torturer(self, aiclient, card):
        AnswerEvent(aiclient.last_info.answers[1]).post(aiclient.ev)
        
class _BigMoneyStrategy(_Strategy):
    
    def _cards_to_buy_gen(self, aiclient):
##        print [c.__class__.__name__ for c in aiclient.deck]
##        print [c.__class__.__name__ for c in aiclient.board]
##        print [c.__class__.__name__ for c in aiclient.hand]
##        print [c.player_name for c in aiclient.players]
##        print [p.card for p in aiclient.boardsetup] #boardsetup contains the random kingdom cards
##        print [p.card for p in aiclient.boardcommon] #boardcommon contains the treasures and victory cards

        if(any(isinstance(card,Market) for card in aiclient.boardsetup)):
            yield Market

##        for p in aiclient.boardsetup + aiclient.boardcommon:
##            yield p.card
            
##        yield aiclient.boardsetup[0].card
            
        yield Copper
        
        if count(aiclient, Gold) >= 2:
            yield Province
        
        yield Gold
        
        if count(aiclient, Gold) < 5 and count(aiclient, Silver) < 6:
            yield Silver

class _AiClient(object):

    def __init__(self, pipe, strategy):
        assert pipe
        
        self.wait_for_event = None
        self.phase = None
        self.subphase = None
        self.connected = False
        self.req_con = False
        self.master = False
        self.start_requested = False
        self.ev = None
        self.deadcounter = 0
        self.running = True
        self.pipe = get_timeout_pipe(pipe)
        self.id = None
        self.last_id = 0
        self.board = [] #bot's cards on the board (cards played so far)
        self.deck = [] #all bot's cards
        self.hand = [] #the bot's hand
        self.players = [] 
        self.strategy = strategy
        
    @property
    def active_player(self):
        if self.players:
            return next((p for p in self.players if p.current), None)

    @property
    def player(self):
        if self.players:
            return next((p for p in self.players if p.id == self.id), None)

    def get_pile(self, cardtype):
        piles = list(chain(self.boardsetup, self.boardcommon))
        return next(p for p in piles if p.card == cardtype)

    def discard_crap(self, count):
        gen = _crap_generator(self)
        cards = [next(gen).id for _ in xrange(count)]
        AnswerEvent(cards).post(self.ev)

    def wait(self, event):
        self.wait_for_event = event
        
    def handle_connectionsuccess(self, event):
        self.id = int(event.id)
        RequestChangeName("[bot] %s" % get_random_name()).post(self.ev)

    def handle_setmasterevent(self, event):
        self.master = event.master

    def handle_connectionfailed(self, event):
        logging.debug("connection failed")

    def handle_newhandevent(self, event):
        self.hand = event.hand
        self.deck = event.deck
        #logging.debug("AICLIENT got hand %s", " ".join([str(c.id) for c in self.hand]))
        
    def handle_newboardsetupevent(self, event):
        self.boardsetup = event.boardsetup
        
    def handle_newboardevent(self, event):
        self.board = event.board
    
    def handle_newdeckevent(self, event):
        self.deck = event.deck
        
    def handle_newboardcommonevent(self, event):
        self.boardcommon = event.boardcommon
           
    def handle_tickevent(self, event):
        if not self.req_con:
            addr = find_server()
            RequestConnectEvent(addr[0], int(addr[1])).post(self.ev)
            self.req_con = True

        if not self.pipe.check():
            self.pipe.send([PP_QUIT])
            QuitEvent().post(self.ev)

    def handle_endgameevent(self, event):
        logging.debug(event.result)

    def handle_phasechangedevent(self, event):
        self.phase = event.phase
        
    def handle_subphasechangedevent(self, event):
        self.subphase = event.subphase
        self.last_id = event.subid
        self.last_info = event.info
       
    def handle_playerinfoevent(self, event):
        self.players = event.playerinfos
        if self.master and len(self.players) == 3:
            if not self.start_requested:
                RequestStartGame().post(self.ev)
                self.start_requested = True

    def buy_card(self, cardclass):
        BuyCardEvent(self.get_pile(cardclass).id).post(self.ev)
            
    def do_action(self):
        self.wait(PhaseChangedEvent)

        print [c for c in self.hand.cards if c.cardtype == ACTION]
        card = next((c for c in self.hand.cards if c.cardtype == ACTION), None)
        if card:
            logging.debug("playing action %s %i", card, card.id)
            PlayCardEvent(card.id).post(self.ev)

        if not card:
            EndPhaseEvent(P_ACTION).post(self.ev)
        return 
    
    def do_buy(self):
        t = [c for c in self.hand if c.cardtype & TREASURE]
        if t:
            card = next(c for c in t)
            logging.debug("playing card %s", str(card.name))
            PlayCardEvent(card.id).post(self.ev)
            self.wait(PlayerInfoEvent)
            return 
        
        card = self.strategy.choose_card_to_buy(self)
        if card:
            time.sleep(0.2)
            self.buy_card(card)
        else:
            EndPhaseEvent().post(self.ev)
        self.wait(PhaseChangedEvent)
        # AI wont buy cards because automatic skipping of action phase
        
    def answercard(self, card):
        logging.debug("handle... %s %i", self.board[-1], self.last_id)
        if not card:
            logging.debug("Don't know what this is")
            return
        
        self.strategy.handle_card(self, card)
        
    def get_card(self):
        return next((c for c in self.board if c.id == self.last_id), None)
        
    def notify(self, event):
        if any(isinstance(event, e) for e in (PlayCardEvent, 
                                              BuyCardEvent, 
                                              TickEvent,
                                              EndPhaseEvent)):
##            logging.debug("Ignoring event %s",event)
##            logging.debug("Event dir %s",dir(event))
            return
        
        if self.subphase in (SP_PICKCARDSFROMHAND, SP_ASKPLAYER):
            card = self.get_card()
            self.answercard(card)
        
        if self.wait_for_event:
            if not isinstance(event, self.wait_for_event):
                return
            
        self.wait_for_event = None
        
        if not self.active_player is self.player:
            return

        if self.subphase != SP_PLAYERINPUT:
            return
        
        if self.phase == P_ACTION:
            self.do_action()
            
        if self.phase == P_BUY:
            self.do_buy()
