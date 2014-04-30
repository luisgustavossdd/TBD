'''
Created on Apr 28, 2014

@author: LuisGustavo
'''
from game.cards.common import *
from game.cards.base import *
from game.cards.intrigue import *

from client.aiclient.Strategy import canBuy

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
            self.gameEnded = False
            if self.board.has_key(Curse): self.board.pop(Curse)
            if self.board.has_key(Copper): self.board.pop(Copper)
            if not any([card.cost[1] for card in self.board]) and self.board.has_key(Potion): self.board.pop(Potion)
            
    
    @staticmethod
    def isInitied():
        return DominionGameState.initied
    
    @staticmethod
    def reset():
        DominionGameState.states = None
        DominionGameState.players = None
        DominionGameState.numPlayers = None
        DominionGameState.initied = False
        
    
    def getAlpha(self):
        return 1.0/(1.0 + self.visits)
    
    def nextPlayer(self):
        self.playerIndex = (self.playerIndex+1)%DominionGameState.numPlayers
        return DominionGameState.players[self.playerIndex]
    
    def isEqual(self,other):
        sameBoard = self.board == other.board
        sameDecks = self.cards == other.cards
#         sameDecks = all([sorted(self.cards[player].values()) == sorted(other.cards[player].values()) for player in DominionGameState.players])
        return (sameBoard and sameDecks)
    
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
        
#         for state in DominionGameState.states:
#             if state.isEqual(successor) : 
#                 return state
            
        DominionGameState.states += [successor]            
        return successor
        
    def GetMoves(self):
        """ Get all possible moves from this state.
        """
#         SolveHand?
#         return [card for card in self.board.keys() if canBuy(card,moneyAvailable(self.playerJustMoved))]
        self.GetResult(self.playerJustMoved)
        if self.gameEnded: return [None]
        return [card for (card, amount) in self.board.items() if amount and card.knowHowUse()]
    
    def GetResult(self, playerjm):
        """ Get the game result from the viewpoint of playerjm. 
        """
        # Return only if the game ended?
        myScore = sum([card.getVictoryPoints() for card in self.cards[playerjm]])
#         otherMaxScore = max([sum([card.getVictoryPoints() for card in self.cards[player]]) for player in self.players if not player == playerjm])
        otherMaxScore = 0
        
        noProvinces = self.board[Province] == 0
        threePilesEmpty = ([cardCount for cardCount in self.board.values()]).count(0) >= 3
        
        self.gameEnded = noProvinces or threePilesEmpty
        
        #returning only when game is over...shoud return in any state?
        return (myScore - otherMaxScore) if self.gameEnded else None