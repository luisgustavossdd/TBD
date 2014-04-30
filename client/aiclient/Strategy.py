'''
Created on Apr 28, 2014

@author: LuisGustavo
'''
from framework.event import *
from game.cards.common import *
from game.cards.base import *
from game.cards.intrigue import *
from game.cards.card import ACTION, TREASURE

from client.aiclient.util.Learning import QLearning
from client.aiclient.Policy import DominionPolicy

def can_afford(aiclient, card):
    return aiclient.player.money >= card.cost[0] and aiclient.player.potion >= card.cost[1]  

def canBuy(card,money):
    return all([valueCard <= valueMoney for valueCard,valueMoney in zip(*[card.cost,money])])


class _Strategy(object):
    
    def __init__(self, policy):
        self.policy = policy
    
    def _cards_to_buy_gen(self, money):
        for card in sorted(self.policy.cards(), key= lambda x: (x.cost, x.getMoney(), x.getBonus(), x.getVictoryPoints()), reverse= True):
            if canBuy(card, money):
                yield card
    
    def choose_card_to_buy(self, money):
        gen = self._cards_to_buy_gen(money)
        return next((c for c in gen if canBuy(c, money)), None)
    
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
        
    def getPolicy(self):
        return self.QLeaner.getPolicy();