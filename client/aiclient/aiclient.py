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
from game.pile import *

from client.aiclient.util.Learning import QLearning

import operator

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

def moneyAvailable(aiclient): 
    return (0,0) if not len(aiclient.hand.cards) or not len(aiclient.board.cards) else map(sum,zip(*[card.getMoney() for card in aiclient.hand.cards + aiclient.board.cards]))

def canBuy(card,money):
    return all([valueCard <= valueMoney for valueCard,valueMoney in zip(*[card.cost,money])])

def sub(current,price): 
    return tuple(map(operator.sub,current,price))

samePile = lambda self,other: all([selfCard == otherCard for (selfCard,otherCard) in zip(*[sorted(self.cards,key=lambda card:card.name),sorted(other.cards,key=lambda card:card.name)])])
sameCards = lambda self,other: all([selfCard == otherCard for (selfCard,otherCard) in zip(*[sorted(self,key=lambda card:card.name),sorted(other,key=lambda card:card.name)])]) 
samePiles = lambda self,other: all(samePile(selfPile,otherPile) for (selfPile,otherPile) in zip(*[sorted(self,key=lambda pile: pile.name),sorted(other,key=lambda pile: pile.name)]))

class DominionGameState:

    states = None
    players = None
    numPlayers = None
    initied = False
    
    def __init__(self, player, board, cards, players = None):
        
            if not DominionGameState.players: 
                DominionGameState.players = players
                DominionGameState.numPlayers = len(players)
                self.cards = dict(zip(*[DominionGameState.players, DominionGameState.numPlayers * [cards]]))
                DominionGameState.initied = True
                cards = None
                
            if not DominionGameState.states: 
                DominionGameState.states = [self]
                
            self.playerJustMoved = player
            self.playerIndex = DominionGameState.players.index(player)
            self.board = board #keys: kingdom's cards #values: quantity
            self.cards = cards if cards else self.cards #keys: players         #values: player's cards
            self.visits = 0
    
    @staticmethod
    def isInitied():
        return DominionGameState.initied
    
    def getAlpha(self):
        return 1.0/(1.0 + self.visits)
    
    def nextPlayer(self):
        self.playerIndex = (self.playerIndex+1)%DominionGameState.numPlayers
        return DominionGameState.players[self.playerIndex]
    
    def isEqual(self,other):
        sameBoard = self.board == other.board
        sameDecks = self.cards == other.cards
#         sameDecks = all([sorted(self.cards[player].values()) == sorted(other.cards[player].values()) for player in DominionGameState.players])
        return sameBoard and sameDecks
    
    def Clone(self):
        """ Create a deep clone of this game state.
        """
        return DominionGameState(self.playerJustMoved, self.board.copy(), self.cards.copy())

    def DoMove(self, move):
        """ Update a state by carrying out the given move.
            Must update playerJustMoved.
        """
#         self.playerJustMoved = self.nextPlayer()
        if not move: return
        self.board[move] -= 1
        self.cards[self.playerJustMoved] += [move]
            
    def generateSuccessor(self,move):
        
        successor = self.Clone()
        successor.DoMove(move)
        
        for state in DominionGameState.states:
            if state.isEqual(successor) : return state
            
        DominionGameState.states += [successor]            
        return successor
        
    def GetMoves(self):
        """ Get all possible moves from this state.
        """
#         SolveHand?
#         return [card for card in self.board.keys() if canBuy(card,moneyAvailable(self.playerJustMoved))]
        return [card for (card, amount) in self.board.items() if amount] + [None]
    
    def GetResult(self, playerjm):
        """ Get the game result from the viewpoint of playerjm. 
        """
        # Return only if the game ended?
        myScore = sum([card.getVictoryPoints() for card in self.cards[playerjm]])
#         otherMaxScore = max([sum([card.getVictoryPoints() for card in self.cards[player]]) for player in self.players if not player == playerjm])
        otherMaxScore = 0
        
        noProvinces = len(playerjm.get_pile(Province).cards) == 0
        threePilesEmpty = ([cardCount for cardCount in self.board.values()]).count(0) >= 3
        
        self.gameEnded = noProvinces or threePilesEmpty
        
        #returning only when game is over...shoud return in any state?
        return (myScore - otherMaxScore) if self.gameEnded else None
        
class DominionPolicy:
    def __init__(self, cardsToBuy):
        self.cardsToBuy = cardsToBuy

    def cards(self):
        return sorted([card for (card,amount) in self.cardsToBuy.items() if amount],key=lambda card: card.cost, reverse=True)

class _Strategy(object):
    
    def __init__(self, policy):
        self.policy = policy
    
    def _cards_to_buy_gen(self, aiclient):
        for card in self.policy.cards():
#             if canBuy(card,moneyAvailable(aiclient)):
            if canBuy(card,aiclient.money):
                self.policy.cardsToBuy[card] -= 1
                yield card
    
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
    def __init__(self):
        _Strategy.__init__(self, DominionPolicy({Gold:2, Province:8, Silver:6}))

class QLearnerStrategy(_Strategy):
    def __init__(self, initialState):
        self.QLeaner = QLearning()
        self.QLeaner.learn(initialState)
        _Strategy.__init__(self, self.QLeaner.getPolicy())

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
        self.board = Pile() #bot's cards on the board (cards played so far)
        self.deck = [] #all bot's cards
        self.hand = Pile() #the bot's hand
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
#         print "Player:",self.id
#         print "hand ",[card.__class__.__name__ for card in event.hand]
#         print "deck ",[card.__class__.__name__ for card in event.deck]
        self.hand = event.hand
        self.deck = event.deck
        #logging.debug("AICLIENT got hand %s", " ".join([str(c.id) for c in self.hand]))
        
    def handle_newboardsetupevent(self, event):
#         print "board  ",[(pile.cards[0].__class__.__name__,len(pile.cards)) for pile in event.boardsetup]
        self.boardsetup = event.boardsetup
        
    def handle_newboardevent(self, event):
#         print "board ",[card.__class__.__name__ for card in event.board]
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

#         print [c for c in self.hand.cards if c.cardtype == ACTION]
        card = next((c for c in self.hand.cards if c.cardtype == ACTION), None)
        if card:
            logging.debug("playing action %s %i", card, card.id)
            PlayCardEvent(card.id).post(self.ev)

        if not card:
            EndPhaseEvent(P_ACTION).post(self.ev)
        return 
    
    def do_buy(self):
        self.money = moneyAvailable(self)
        
        t = [c for c in self.hand if c.cardtype & TREASURE]
        if t:
            card = next(c for c in t)
            logging.debug("playing card %s", str(card.name))
            PlayCardEvent(card.id).post(self.ev)
            self.wait(PlayerInfoEvent)
            return
        
        gameState = None
        if not DominionGameState.isInitied(): 
#             player  = next((p for p in self.players if p.id == self.id), None)
#             players = self.players
            player  = self
            players = [player]
            board   = dict([(pile.cards[0].__class__,len(pile.cards)) for pile in self.boardsetup] + [(pile.cards[0].__class__,len(pile.cards)) for pile in self.boardcommon])
            cards   = [card.__class__ for card in self.hand.cards] + [card.__class__ for card in self.deck.cards]
            gameState = DominionGameState(player, board, cards, players)
            QLeaner = QLearning()
            QLeaner.learn(gameState)
            self.strategy = _Strategy(DominionPolicy(QLeaner.getPolicy()))
#             logging.debug( "Q: %s", QLeaner.Q)
#             logging.debug( "states created: %s", len(DominionGameState.states))
# #             logging.debug( "actions visited: %s", QLeaner.cards)
            logging.debug( "Policy: %s", QLeaner.getPolicy())
#             self.strategy.init(gameState)

        buysLeft = 1 + sum([card.getBonusBuys() for card in self.board] + [card.getBonusBuys() for card in self.hand])
        while buysLeft:
            card = self.strategy.choose_card_to_buy(self)
            if card:
                time.sleep(0.2)
                self.buy_card(card)
                self.money = sub(self.money, card.cost)
                buysLeft -= 1
            else:
                break
        EndPhaseEvent().post(self.ev)
        
#         card = self.strategy.choose_card_to_buy(self)
#         if card:
#             time.sleep(0.2)
#             self.buy_card(card)
#         else:
#             EndPhaseEvent().post(self.ev)
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
    
        
