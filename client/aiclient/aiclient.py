#!/usr/bin/python
# -*- coding: utf-8 -*-

import copy
import os
import time
from itertools import chain
import itertools
import random
from math import *

from framework.event import *
from game.gamestates import SP_PLAYERINPUT, P_BUY, P_ACTION,\
    SP_PICKCARDSFROMHAND, SP_ASKPLAYER
##from game.cards.common import Province, Gold, Silver
from game.cards.common import *
from game.cards.base import *
from game.cards.intrigue import *
from game.cards import common

from framework.async import PP_QUIT, get_timeout_pipe
from framework.networking import find_server
import logging
import random
from game.cards.card import ACTION, TREASURE
from game.pile import *

import operator

from client.aiclient.util.Learning import QLearning
from client.aiclient.Policy import DominionPolicy
from client.aiclient.Strategy import *
from client.aiclient.GameState import DominionGameState

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
    strat = None
    is_utc = None
    if random.randrange(0, 2) > 0:
        print "_UCB1_MCTS_Strategy Bot"
        is_utc = 1
        strat = _UCB1_MCTS_Strategy(None)
    else:
        print "QLearning Bot"
    return _AiClient(pipe, strat, is_utc)

def _crap_generator(aiclient):
    for c in (c for c in aiclient.hand if c.name in ("Duchy", "Province", "Estate")):
        yield c
    actions = [c for c in aiclient.hand if c.cardtype & ACTION] 
    if len(actions) > 3:
        for c in actions[:2]:
            yield c
    for c in aiclient.hand:
        yield c

def count(aiclient, card):
    return len([c for c in aiclient.deck if isinstance(c, card)])

def moneyAvailable(aiclient): 
    return (0,0) if not len(aiclient.hand.cards) or not len(aiclient.board.cards) else map(sum,zip(*[card.getMoney() for card in aiclient.hand.cards + aiclient.board.cards]))

def sub(current,price): 
    return tuple(map(operator.sub,current,price))

class _Strategy(object):
    
    def __init__(self, policy):
        self.policy = policy
    
    def _cards_to_buy_gen(self, aiclient):
        for card in self.policy.cards():
            if canBuy(card,aiclient.money):
                self.policy.cardsToBuy[card] -= 1
                yield card
    
    def choose_card_to_buy(self, aiclient):
        gen = self._cards_to_buy_gen(aiclient)
        return next((c for c in gen if can_afford(aiclient, c)), None)
    
    def handle_card(self, aiclient, card):
        
        handler = getattr(self, '_handle_card_' + card.name.lower())
        if handler not in dir(self): return
        handler(aiclient, card)
        
    def _handle_card_militia(self, aiclient, card):
        num_hand = len(aiclient.hand)
        aiclient.discard_crap(num_hand - 3)
    
    def _handle_card_torturer(self, aiclient, card):
        AnswerEvent(aiclient.last_info.answers[1]).post(aiclient.ev)


class _UCB1_MCTS_Strategy(_Strategy):
    
    def choose_card_to_buy(self, aiclient):
        sim_state = self.UCB1_State([aiclient.hand.cards, aiclient.deck.cards, aiclient.players, aiclient.assumed_player_decks, 
                                      aiclient.gain_deck, aiclient.boardsetup, aiclient.boardcommon, aiclient.prev_game_piles, 
                                      aiclient.prev_players, aiclient.player, aiclient.my_index])
        move = self.UCT(sim_state, 5, True)
        return move


    def UCT(self, rootstate, itermax, verbose = False):
        rootnode = self.Node(state = rootstate)
        for i in range(itermax):
            node = rootnode
            state = rootstate.clone()
            while node.untriedMoves == [] and node.childNodes != []:
                node = node.UCTSelectChild()
                state.do_move(node.move)
            
            if node.untriedMoves != []:
                m = random.choice(node.untriedMoves)
                state.do_move(m)
                node = node.AddChild(m,state)
            
            while state.get_moves() != []:
                state.do_move(random.choice(state.get_moves())) 
            
            while node != None:
                node.Update(state.get_result(node.playerJustMoved))
                node = node.parentNode
            
        if (verbose): print rootnode.TreeToString(0)
        else: print rootnode.ChildrenToString()
        return sorted(rootnode.childNodes, key = lambda c: c.visits)[-1].move         


    class Node:
        
        def __init__(self, move = None, parent = None, state = None):
            self.move = move # the move that got us to this node - "None" for the root node
            self.parentNode = parent # "None" for the root node
            self.childNodes = []
            self.wins = 0
            self.visits = 0
            self.untriedMoves = state.get_moves()
            self.playerJustMoved = state.playerJustMoved
            
        def UCTSelectChild(self):
            s = sorted(self.childNodes, key = lambda c: c.wins/c.visits + sqrt(2*log(self.visits)/c.visits))[-1]
            return s
        
        def AddChild(self, m, s):
            n = _UCB1_MCTS_Strategy.Node(move = m, parent = self, state = s)
            self.untriedMoves.remove(m)
            self.childNodes.append(n)
            return n
        
        def Update(self, result):
            self.visits += 1
            self.wins += result
        
        def __repr__(self):
            return "[M:" + str(self.move) + " W/V:" + str(self.wins) + "/" + str(self.visits) + " U:" + str(self.untriedMoves) + "]"
        
        def TreeToString(self, indent):
            s = self.IndentString(indent) + str(self)
            for c in self.childNodes:
                s += c.TreeToString(indent+1)
            return s
        
        def IndentString(self,indent):
            s = "\n"
            for i in range (1,indent+1):
                s += "| "
            return s
        
        def ChildrenToString(self):
            s = ""
            for c in self.childNodes:
                s += str(c) + "\n"
            return s
        
    
    class UCB1_State(object):
        
        def __init__(self, info):
            self.info = []
            for item in info:
                self.info.append(copy.deepcopy(item))
            self.player_index = info[len(info) - 1]
            self.num_players = len(info[2])
            self.playerJustMoved = self.player_index - 1 if self.player_index > 0 else self.num_players - 1
                                    
        def clone(self):
            clone_state = _UCB1_MCTS_Strategy.UCB1_State(self.info)
            return clone_state
        
        def assert_on_piles(self, kingdom_plies, common_piles, prev_piles):
            empty_count = 0
            for pile in kingdom_plies:
                if len(pile.cards) == 0:
                    empty_count += 1
                if empty_count == 3:
                    return False
            for pile in common_piles:
                if len(pile.cards) == 0:
                    empty_count += 1
                    if empty_count == 3:
                        return False
            pro_point = 0
            for i in range(len(prev_piles[1])):
                cur_pile_cards = prev_piles[1][i].cards
                if(cur_pile_cards != []):
                    if cur_pile_cards[0].name == "Province":
                        pro_point = i
            if len(common_piles[pro_point].cards) == 0:
                return False
            return True
        
        def get_result(self, playerjm):
            points = []
            player_id = self.info[2][playerjm].id
            player_deck = self.info[3][player_id]
            my_points = self.calc_score(player_deck)
            for key in self.info[3].iterkeys():
                if(key != player_id):
                    points.append(self.calc_score(self.info[3][key]))
            for i in range(len(points)):
                if my_points < points[i]:
                    return 0
            return 1
        
        def calc_score(self, deck):
            vp_points = 0
            for card in deck:
                if isinstance(card, tuple) or isinstance(card, list):
                    card = card[0]
                if(card.name == "Estate"):
                    vp_points += 1
                if(card.name == "Duchy"):
                    vp_points += 3
                if(card.name == "Province"):
                    vp_points += 6
                if(card.name == "Great Hall"):
                    vp_points += 1
                if(card.name == "Duke"):
                    for other_card in deck:
                        while isinstance(other_card, tuple) or isinstance(other_card, list):
                            other_card = other_card[0]
                        if(other_card.name == "Duchy"):
                            vp_points += 1
                if(card.name == "Gardens"):
                    vp_points += (len(deck) // 10)
                
            
        def get_moves(self):
            moves = []
            if self.assert_on_piles(self.info[5], self.info[6], self.info[7]):
                act_cards = []
                board_cards = []
                cur_player_hand = self.info[0]
                print ""
                print cur_player_hand
                print ""
                for card in cur_player_hand:
                    while isinstance(card, tuple) or isinstance(card, list):
                        card = card[0]
                    if not 0 is (card.cardtype & ACTION):
                        act_cards.append(card)
                    if not 0 is (card.cardtype & TREASURE):
                        board_cards.append(card)
                full_act_plays = {}
                for act_card in act_cards:
                    temp_hand = copy.deepcopy(act_cards)
                    removal_card = [a_card for a_card in temp_hand if a_card.name == act_card.name][0]
                    i = 0
                    for j in range(len(temp_hand)):
                        if temp_hand[j].name == removal_card.name:
                            i = j
                            break
                    del temp_hand[i]
                    full_act_plays[act_card] = self.generate_full_acts(act_card, temp_hand) 
                num_extra_resources = {}
                money = self.info[2][self.player_index].money
                potion = self.info[2][self.player_index].potion
                for card in board_cards:
                    money += treasure_card_worth.get(card.name, (0, 0))[0]
                    potion +=  treasure_card_worth[card.name][1]
                buy_cards = []
                for kingdom_pile in self.info[5]:
                    if kingdom_pile.cards != []:
                        if kingdom_pile.cards[0].name in ap_cards:
                            buy_cards.append(kingdom_pile.cards[0])
                for common_pile in self.info[6]:
                    if common_pile.cards != []:
                        buy_cards.append(common_pile.cards[0])
                if act_cards != []:
                    for key in full_act_plays.iterkeys():
                        num_extra_resources[key] = self.calc_extra_resources(full_act_plays[key])
                        print num_extra_resources[key]
                        if(num_extra_resources[key] != []):
                            for i in range(len(num_extra_resources[key])):
                                play_money = num_extra_resources[key][i][0] + money + act_card_bonuses[key.name][0]
                                play_potions = num_extra_resources[key][i][1] + potion + act_card_bonuses[key.name][1]
                                play_buys = num_extra_resources[key][i][2] + self.info[2][self.player_index].buys + act_card_bonuses[key.name][3]
                                print [play_money, play_potions, play_buys]
                                full_buys = self.generate_full_buys(play_money, play_potions, play_buys, buy_cards)
                                for buys in full_buys:
                                    primary_action_card = key
                                    extra_action_cards = full_act_plays[primary_action_card][0]
                                    print [key, extra_action_cards, buys]
                                    moves.append([primary_action_card, extra_action_cards, buys])
                                full_act_plays[key] = full_act_plays[key][1:]
                        else:
                            full_buys = self.generate_full_buys(money, potion, self.info[2][self.player_index].buys, buy_cards)
                            for buys in full_buys:
                                moves.append([key, (), buys])
                            print full_buys
                else:
                    full_buys = self.generate_full_buys(money, potion, self.info[2][self.player_index].buys, buy_cards)
                    for buys in full_buys:
                        moves.append([None, (), buys])
            return moves
        
        def do_move(self, move):
            prev_piles = (copy.deepcopy(self.info[5]), copy.deepcopy(self.info[6]))
            buy_cards = move[2]
            for card in buy_cards:
                self.info[1].append(buy_cards)
                for pile in self.info[5]:
                    if(pile.cards != []):
                        if(pile.cards[0].name == card.name):
                            pile.cards = pile.cards[1:]
                for pile in self.info[6]:
                    if(pile.cards != []):
                        if(pile.cards[0].name == card.name):
                            pile.cards = pile.cards[1:]

            self.info[3][self.info[2][self.player_index].id] = self.info[1]
            new_player_index = (self.player_index + 1) % self.num_players
            self.info[len(self.info) - 1] = new_player_index
            self.info[7] = prev_piles
            new_id = self.info[2][new_player_index].id
            new_deck = self.info[3][new_id]
            new_hand = self.gen_rand_hand(new_deck)
            self.info[0] = new_hand
            self.info[1] = new_deck
            return
        
        def gen_rand_hand(self, deck):
            tmp_deck = copy.deepcopy(deck)
            new_deck = []
            while len(new_deck) < 5:
                rander = random.randrange(0, len(tmp_deck) - 1)
                card = tmp_deck[rander]
                tmp_deck.remove(card)
                new_deck.append(card)
            return new_deck
        
        def calc_extra_resources(self, act_card_tuples_list):
            extra_resources = []
            for play in act_card_tuples_list:
                cur_extra_money = 0
                cur_extra_potion = 0
                cur_extra_buys = 0
                for card in play:
                    if act_card_bonuses.has_key(card.name):
                        cur_extra_money += act_card_bonuses[card.name][0]
                        cur_extra_potion += act_card_bonuses[card.name][1]
                        cur_extra_buys += act_card_bonuses[card.name][3]
                extra_resources.append([cur_extra_money, cur_extra_potion, cur_extra_buys])
            return extra_resources
            
            
        def generate_full_acts(self, act_card, other_act_cards):
            extra_acts = act_card_bonuses.get(act_card.name, (0, 0, 0))[2]
            if(extra_acts > 0):
                if(len(other_act_cards) < extra_acts):
                    return list(itertools.combinations(other_act_cards, len(other_act_cards)))
                else:
                    return list(itertools.combinations(other_act_cards, extra_acts))
            return []
            
        def generate_full_buys(self, money, potions, buys, buy_cards):
            real_buy_cards = []
            full_buys = []
            for card in buy_cards:
                if card.cost[0] <= money and card.cost[1] <= potions:
                    real_buy_cards.append(card)
            buy_sets = list(itertools.combinations(real_buy_cards, buys))
            for buy_subset in buy_sets:
                if(self.pass_appraisal(buy_subset, money, potions)):
                    full_buys.append(buy_subset)
            return full_buys
            
        def pass_appraisal(self, cards_to_buy, money, potions):
            for card in cards_to_buy:
                money -= card.cost[0]
                potions -= card.cost[1]
                if money < 0 or potions < 0:
                    return False
            return True

class _AiClient(object):

    def __init__(self, pipe, strategy, utc = None):
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
        self.assumed_player_decks = {}
        self.gain_deck = []
        self.prev_game_piles = []
        self.prev_players = []
        self.my_index = 0
        self.utc = utc
        
    def init_gamestate(self):
        if not DominionGameState.isInitied():
            player  = self
            players = [player]
            cards   = [card.__class__ for card in self.hand.cards] + [card.__class__ for card in self.deck.cards]
            board   = dict([(pile.cards[0].__class__,len(pile.cards)) for pile in self.boardsetup] + [(pile.cards[0].__class__,len(pile.cards)) for pile in self.boardcommon])
            
            self.strategy = QLearnerStrategy(DominionGameState(player, board, cards, players))
            logging.debug( "Policy: %s", self.strategy.getPolicy())
        
    @property
    def active_player(self):
        if self.players:
            return next((p for p in self.players if p.current), None)

    @property
    def player(self):
        if self.players:
            return next((p for p in self.players if p.id == self.id), None)

    def get_pile(self, cardtype):
        if not isinstance(self.strategy, _UCB1_MCTS_Strategy):
            piles = list(chain(self.boardsetup, self.boardcommon))
            return next(p for p in piles if p.card == cardtype)
        else:
            piles = list(chain(self.boardsetup, self.boardcommon))
            return next(p for p in piles if p.card.name == cardtype.name)

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
#         print "Player:",self.id
#         print "hand ",[card.__class__.__name__ for card in event.hand]
#         print "deck ",[card.__class__.__name__ for card in event.deck]
        #logging.debug("AICLIENT got hand %s", " ".join([str(c.id) for c in self.hand]))
        
    def handle_newboardsetupevent(self, event):
        self.boardsetup = event.boardsetup
#         print "board  ",[(pile.cards[0].__class__.__name__,len(pile.cards)) for pile in event.boardsetup]
        
    def handle_newboardevent(self, event):
        self.board = event.board
#         print "board ",[card.__class__.__name__ for card in event.board]
    
    def handle_newdeckevent(self, event):
        self.deck = event.deck
        
    def handle_newboardcommonevent(self, event):
        self.boardcommon = event.boardcommon
        if self.utc == None and not isinstance(self.strategy, _UCB1_MCTS_Strategy):
            self.init_gamestate()
           
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
        if not isinstance(self.strategy, _UCB1_MCTS_Strategy):
            player = [p for p in self.players if p.id == self.id][0]
            action_cards = [c for c in self.hand.cards if c.cardtype == ACTION]
            for card in action_cards:
                if not player.actions: break
                if card:
                    logging.debug("playing action %s %i", card, card.id)
                    PlayCardEvent(card.id).post(self.ev)
                    player.actions-=1
                else:
                    break
        else:
            global seter
            global first_play
            global re_seter
            global cards_to_play
            card = None
            if not seter:
                seter = True
                self.gen_first_cards(self.players)
                self.prev_players = copy.deepcopy(self.players)
                self.index_of_self()
            elif seter and first_play == False:
                first_play = True
                if re_seter == False:
                    re_seter = True
                    self.prev_game_piles = [copy.deepcopy(self.boardsetup), copy.deepcopy(self.boardcommon)]
                missing_cards = self.determin_missing_cards([self.boardsetup, self.boardcommon], self.prev_game_piles, self.gain_deck)
                self.prev_game_piles = [copy.deepcopy(self.boardsetup), copy.deepcopy(self.boardcommon)]
                self.update_beliefs(missing_cards, copy.deepcopy(self.players), self.prev_players)
                self.prev_players = copy.deepcopy(self.players)
                cards = self.strategy.choose_card_to_buy(self)
                cards_to_play = cards
                print " "
                print "cards to play", cards_to_play
                print " "
                card = cards_to_play[0]
            if card:
                logging.debug("playing action %s %i", card, card.id)
                PlayCardEvent(card.id).post(self.ev)
            first_play = False

        EndPhaseEvent(P_ACTION).post(self.ev)
        return 
    
    def do_buy(self):
        if not isinstance(self.strategy, _UCB1_MCTS_Strategy):
            t = [c for c in self.hand if c.cardtype & TREASURE]
            if t:
                card = next(c for c in t)
                logging.debug("playing card %s", str(card.name))
                PlayCardEvent(card.id).post(self.ev)
                self.wait(PlayerInfoEvent)
                return
            
            player = [p for p in self.players if p.id == self.id][0]
            self.money = (player.money,player.potion)
            while player.buys and self.money:
                card = self.strategy.choose_card_to_buy(self.money)
                if card:
                    logging.debug("buying card %s", str(card.name))
                    time.sleep(0.2)
                    self.buy_card(card)
                    self.money = sub(self.money, card.cost)
                    player.buys -= 1
                    self.strategy.getPolicy().buy(card)
                else:
                    break
        else:
            global cards_to_play
            t = [c for c in self.hand if c.cardtype & TREASURE]
            if t:
                card = next(c for c in t)
                logging.debug("playing card %s", str(card.name))
                PlayCardEvent(card.id).post(self.ev)
                self.wait(PlayerInfoEvent)
                return
            card = None
            if(cards_to_play != []):
                if(cards_to_play[2] != ()):
                    card = [c for c in cards_to_play[2] if can_afford(self, c)][0]
            if card:
                time.sleep(0.2)
                self.buy_card(card)
                self.gain_deck.append(card)
            
        EndPhaseEvent().post(self.ev)
        self.wait(PhaseChangedEvent)
        
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

    def update_beliefs(self, missing_cards, cur_players, prev_players):
        if missing_cards != []:
            my_id = self.player.id
            cur_other_players = [player for player in cur_players if player.id != my_id]
            prev_other_players = [player for player in prev_players if player.id != my_id]
            for i in range(len(cur_other_players)):
                cur_cards_num = cur_other_players[i].drawpile_size + cur_other_players[i].discardpile_size + cur_other_players[i].hand_size
                prev_cards_num = prev_other_players[i].drawpile_size + prev_other_players[i].discardpile_size + prev_other_players[i].hand_size
                gain_cards_num = cur_cards_num - prev_cards_num
                self.assumed_player_decks[cur_other_players[i].id] = self.assumed_player_decks[cur_other_players[i].id] + missing_cards[:gain_cards_num]
                missing_cards = missing_cards[gain_cards_num:]
            self.assumed_player_decks[self.player.id] = self.deck

    def gen_first_cards(self, players):
        for other_player in players:
            if(other_player.id != self.player.id):
                player_pile = []
                for j in range(7):
                    player_pile.append(common.Copper())
                for k in range(3):
                    player_pile.append(common.Estate())
                self.assumed_player_decks[other_player.id] = player_pile
        return
    
    
    def determin_missing_cards(self, cur_piles, past_piles, gain_deck):
        missing_cards = []
        for i in range(len(cur_piles[0])):
            missing_cards_num = len(past_piles[0][i].cards) - len(cur_piles[0][i].cards) 
            for j in range(missing_cards_num):
                missing_cards.append(past_piles[0][i].cards[0])
        for i in range(len(cur_piles[1])):
            missing_cards_num = len(past_piles[1][i].cards) - len(cur_piles[1][i].cards)
            for j in range(missing_cards_num):
                missing_cards.append(past_piles[1][i].cards[0])
        for miss_card in missing_cards:
            for gain_card in gain_deck:
                if gain_card.name == miss_card.name:
                    missing_cards.remove(miss_card)
                    gain_deck.remove(gain_card)
                    break
        return missing_cards

    def index_of_self(self):
        my_id = self.player.id
        for i in range(len(self.players)):
            if(self.players[i].id == my_id):
                self.my_index = i
                break
        
first_play = False
seter = False
re_seter = False
cards_to_play = []

act_card_bonuses = {}
act_card_bonuses["Woodcutter"] = (2, 0, 0, 1)
act_card_bonuses["Council Room"] = (0, 0, 0, 1)
act_card_bonuses["Village"] = (0, 0, 2, 0)
act_card_bonuses["Market"] = (1, 0, 1, 1)
act_card_bonuses["Laboratory"] = (0, 0, 1, 0)
act_card_bonuses["Bag of Gold"] = (0, 0, 1, 0)
act_card_bonuses["Diadem"] = (2, 0, 0, 0)
act_card_bonuses["Princess"] = (0, 0, 0, 1)
act_card_bonuses["Nomad Camp"] = (2, 0, 0, 1)
act_card_bonuses["Cache"] = (3, 0, 0, 0) #2 coppers
act_card_bonuses["Conspirator"] = (2, 0, 0, 0)
act_card_bonuses["Shanty Town"] = (0, 0, 2, 0)
act_card_bonuses["Bridge"] = (1, 0, 0, 1)
act_card_bonuses["Great Hall"] = (0, 0, 1, 0) 
act_card_bonuses["City"] = (0, 0, 2, 0)
act_card_bonuses["Workers Village"] = (0, 0, 2, 1)
act_card_bonuses["Caravan"] = (0, 0, 1, 0)
act_card_bonuses["Bazaar"] = (1, 0, 2, 0)
act_card_bonuses["Fishing Village"] = (1, 0, 2, 0)

treasure_card_worth = {}
treasure_card_worth["Copper"] = (1, 0)
treasure_card_worth["Silver"] = (2, 0)
treasure_card_worth["Gold"] = (3, 0)
treasure_card_worth["Potion"] = (0, 1)
treasure_card_worth["Diadem"] = (2, 0)
treasure_card_worth["Cache"] = (3, 0)
treasure_card_worth["Harem"] = (2, 0)
ap_cards = ["Copper", "Silver", "Gold", "Potion", "Curse", "Estate", "Duchy", "Province", "Curse",
            "Woodcutter", "Council Room", "Village", "Market", "Moat", "Witch", "Gardens", "Laboratory", 
            "Smithy", "Bag of Gold", "Fairgrounds", "Diadem", "Princess", "Nomad Camp", "Cache", "Tribute", 
            "Coppersmith", "Harem", "Conspirator", "Shanty Town", "Bridge", "Great Hall", "Duke", "City", 
            "Workers Village", "Bank", "Wharf", "Caravan", "Bazaar", "Merchant Ship", "Tactician", "Fishing Village"]
