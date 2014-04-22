#!/usr/bin/python
# -*- coding: utf-8 -*-

from framework.regnancyexception import PileIsEmptyException, \
    NotEnoughMoneyException, RegnancyException
from gamestates import SP_PLAYERINPUT, SP_WAIT, P_BUY, P_ACTION, \
    P_CLEANUP, P_PRECLEANUP
from phase import ActionPhase, BuyPhase, CleanupPhase, PreCleanupPhase, PhaseManager
from rules import commonpiles, standarddeck, prepare_piles, game_end, get_setup
from itertools import chain
from uuid import uuid4
from gamestates import SP_ASKPLAYER, SP_PICKCARDSFROMHAND, SP_PICKCARD, CANCEL_ATTACK, SP_ORDERCARDS
from askplayerinfo import AskPlayerInfo
from stephandler import StepHandler
from cards.card import ACTION, DURATION, TREASURE, Card
from framework.latecall import LateCall
from collections import defaultdict
from subphaseinfo import YesNoSubPhase, AskSubPhase, SubPhaseInfo
from gametrigger import T_ATTACK, T_GAIN
from triggerinfo import TriggerInfo
from infotoken import InfoToken
from gameinterface import GameInterface
import logging
from framework.event import ChangePhaseEvent, ChangeSubPhaseEvent,\
    ChangePilesEvent, ChangeBoardEvent, ChangeHandEvent, MessageEvent,\
    PlayerInfoEvent, GameEndEvent

PROMOTE = 0
BOARD = 1
HAND = 2
PILES = 3
PLAYERINFO = 4
PHASE = 5
MESSAGE = 6
END = 7
SUBPHASE = 8


class Game(GameInterface):

    def __init__(self, ev):
        self.running = False
        self.ev = ev
        self._active_player = None
        self.subphaseinfo = SubPhaseInfo(SP_PLAYERINPUT)

        # when entering a new subphase, the game waits for 
        # an answer of the player. If entering a second (or more)
        # subphase, this one is put on the stack (LIFO).
        # When the subphase was finished, the game enters
        # the subphase on top of the stack 
        self.subphase_cache = []
        
        # all cards on board get added to this list, and then
        # cleanup_step gets called on each of those cards
        # on P_PRECLEANUP (e.g. Treasury/Walled Village)  
        self.precleanupstack = []
        
        # a card can register a callback in this dictionary
        # via the on_resolve() method. The callback is 
        # called when the card is resolved via the resolved
        # method. This is used e.g. by Throne Room, which
        # will play the second card when the first one
        # is resolved. key: card.id value: callable
        self.resolve_handler = {}

        self.attack_cache = {}
        self.reaction_cache = {}
        self.misc_cache = {}
        self.all_player_action_cache = {}

        self.action_step_handler = []
        self.buy_step_handler = []

        # Instead of a callable or None, a card may return
        # a so called LateCall in one of its handler methods.
        # If so, this LateCall will be called when the subphase
        # is restored, instead of immediately right after the
        # handler method 
        self.late_calls = []

        # some cards need to modify the costs of all other cards.
        # Thus they can register a cost-modifying callable.
        # This callable has to takes (coins, potions) and
        # returns (modified_coins, modified_potions) 
        self.cost_mod = []

        self.last_played_cards = defaultdict(list)
        self.last_gained_cards = defaultdict(list)
        self.last_bought_cards = defaultdict(list)

        self.pending_trigger = defaultdict(list)
        self.running_trigger = None

        self.phase = PhaseManager(self, (ActionPhase(self), BuyPhase(self),
                                  PreCleanupPhase(self), CleanupPhase(self)),
                                  self.__phase_enter, self.__phase_entered,
                                  self.__phase_leave)

    def __phase_enter(self, phase):
        """Called when entering a new game phase"""

        assert phase, "phase is None"
        assert self._active_player, "activeplayer is none"
        
        if not self.running:
            return
        
        if phase.key == P_ACTION:
            for d in (self.last_played_cards, self.last_gained_cards, self.last_bought_cards):
                if self._active_player in d:
                    del d[self._active_player]

        ChangePhaseEvent(self._active_player, phase.key).post(self.ev)
        ChangeSubPhaseEvent(0, self._active_player, SP_WAIT).post(self.ev)
        
    def __phase_entered(self, phase):
        """Called when entering a new game phase"""

        assert phase, "phase is None"
        assert self._active_player, "activeplayer is none"
        
        if not self.running:
            return

        if phase.key == P_PRECLEANUP:
            self.precleanupstack.extend(self._active_player.board)
        else:
            ChangeSubPhaseEvent(0, self._active_player, SP_PLAYERINPUT).post(self.ev)

    def __phase_leave(self, phase):
        """Called when leaving a game phase"""

        if phase.key == P_CLEANUP:
            self.cost_mod = []
            ChangePilesEvent().post(self.ev)
            ChangeHandEvent(self.active_player).post(self.ev)
            
    def play_card(self, player, card_id, free=False, is_duration=False):
        """Let the player play a card"""

        if not player is self.active_player:
            logging.error("won't play %i if player %s is not active", card_id, player.name)
            return
        
        if not card_id in [c.id for c in player.hand]:
            logging.critical("card %i is not in hand of %s", card_id, player.name)
            try:
                card = player.deck.get_card(card_id)
                logging.critical("card is %s", card.name)
            except StopIteration:
                logging.critical("could not find card in player deck")
            logging.critical("hand is %s", ", ".join([str(c.id) for c in player.hand]))    
            raise RegnancyException()
        
        card = next(c for c in player.hand if c.id == card_id)

        if self.phase == P_ACTION and not card.cardtype & ACTION:
            return

        if self.phase == P_BUY and not card.cardtype & TREASURE:
            return
        
        player.play_card(card_id)

        if is_duration:
            card.begin_step(self, player)
        else:
            if card.cardtype & DURATION:
                player.durations.add(card)
            
            if self.phase == P_BUY:
                card.buy_step(self, player)
                (self.last_played_cards)[player].append(card)
                for handler in self.buy_step_handler:
                    handler(self, player, card)
            elif self.phase == P_ACTION:
                card.action_step(self, player)
                (self.last_played_cards)[player].append(card)
                for handler in self.action_step_handler:
                    handler(self, player, card)

        if card.cardtype & ACTION and not free:
            player.actions -= 1
        
        self.update_player(player)

    def add_cost_mod(self, mod):
        self.cost_mod.append(mod)
        ChangePilesEvent().post(self.ev)
        ChangeBoardEvent(self.active_player).post(self.ev)

    def get_cost(self, pile_or_card):
        (coins, potions) = pile_or_card.cost
        for mod in self.cost_mod:
            (coins, potions) = mod(coins, potions)
        return (max(coins, 0), max(potions, 0))

    def buy_card(self, player, pile_id):
        """Let the player buy a card"""

        pile = self.get_pile(pile_id)
            
        if not len(pile):
            raise PileIsEmptyException("Player can't buy card from empty pile")
        if self.get_cost(pile)[0] > player.money:
            raise NotEnoughMoneyException("Player can't buy this card, no money")
        if self.get_cost(pile)[1] > player.potion:
            raise NotEnoughMoneyException("Player can't buy this card, no potion")

        player.money -= self.get_cost(pile)[0]
        player.potion -= self.get_cost(pile)[1]
        player.buys -= 1

        msg = "%s bought %s" % (player.name, pile.name)
        card = self.take_card_from_pile(player, pile, message=msg)
        (self.last_bought_cards)[player].append(card)

    def take_card_from_pile(self, player, pile, safe=False, to_hand=False,
                            to_deck=False, message=None):
        """Let the player pick a card from a pile"""

        if not len(pile):
            if safe:
                return
            raise PileIsEmptyException("Player can't pick card from empty pile")

        card = pile.take()
        return self.take_card(player, card, message, to_hand, to_deck)

    def take_card(self, player, card, message=None, to_hand=False, to_deck=False):
        self.yell(message or "%s took %s" % (player.name, card.name))
        player.take_card(card, to_hand, to_deck)
        card.gain_step(self, player)
        self.update_player(player)
        ChangePilesEvent().post(self.ev)
        if player == self.active_player:
            (self.last_gained_cards)[player].append(card)
        self.raise_trigger(T_GAIN, card, player)
        return card

    def raise_trigger(self, trigger, card, player):
        for p in self.players:
            handler = [t for t in [(c, c.handle_trigger(trigger)) for c in p.hand] if t[1] != None]
            if handler:
                self.pending_trigger[p].extend([TriggerInfo(c, player, card, callback) for c, callback in handler])
   
    def trash_card(self, player, card, silent=False):
        """Let the player trash a card from his hand"""

        player.trash_card(card)
        if not (silent or card.virtual):
            self.yell("%s trashed %s" % (player.name, card.name))
        self.update_player(player)

    def discard_cards(self, cards, player=None):
        player = player or self.active_player
        for c in cards:
            card = c if isinstance(c, Card) else player.hand.get_card(c)
            self.discard_card(player, card)

    def discard_card(self, player, card):
        player.discard_card(card)
        self.yell("%s discarded %s" % (player.name, card.name))
        self.update_player(player)

    def discard_hand(self, player):
        any_cards = len(player.hand) > 0
        for _ in xrange(len(player.hand)):
            self.discard_card(player, (player.hand)[0])
        return any_cards

    def whisper(self, message, player=None):
        """Send a message a player"""

        assert message
        MessageEvent(message, reciever=player or self.active_player).post(self.ev)

    def yell(self, message):
        """Send a message to all players"""

        MessageEvent(message).post(self.ev)

    @property
    def active_player(self):
        """Get the active player"""

        return self._active_player

    @property
    def players(self):
        """Get all players"""

        return self._players

    @property
    def other_players(self):
        return [p for p in self._players if not p is self.active_player]

    @property
    def kingdompiles(self):
        """Get all kingdom card piles"""

        return sorted(self._kingdompiles, key=lambda pile: pile.cost)

    @property
    def commonpiles(self):
        """Get all treasure piles, victory card piles etc."""

        return self._commonpiles

    @property
    def allpiles(self):
        """Get all piles (kingdom cards and common cards)"""

        return list(chain(self.commonpiles, self.kingdompiles))

    def update_player(self, player=None):
        """Sending player info around"""

        def up(p):
            if p == self.active_player:
                ChangeBoardEvent(p).post(self.ev)
                ChangePilesEvent().post(self.ev)
            ChangeHandEvent(p).post(self.ev)
            PlayerInfoEvent([p.create_info() for p in self.players]).post(self.ev)

        if player:
            up(player)
        else:
            for p in self.players:
                up(p)

    def setup(self, setup, players):
        """Setup a a new game"""

        self.__init__(self.ev) # This seems like a bad, bad hack?
        self._players = players
        self._kingdompiles = prepare_piles(get_setup(setup), len(self.players))
        self._commonpiles = prepare_piles(commonpiles, len(self.players))
        self.endcondition = game_end
        self.running = True

        for player in self.players:
            player.actions = 1
            player.buys = 1

            [player.take_card(card) for card in standarddeck()]

            [player.draw_card() for _ in xrange(5)]
            self.update_player(player)
            
            ChangePhaseEvent(player, SP_WAIT).post(self.ev)

        self._active_player = (self._players)[0]
        self.phase.next_phase()

    def get_pile(self, cardtype):
        """Get the pile with the specific cardtype"""

        a = lambda pile: pile.card == cardtype
        b = lambda pile: pile.card.name == cardtype
        c = lambda pile: pile.id == cardtype
        
        for l in (a, b, c):
            try:
                return next(pile for pile in self.allpiles if l(pile))
            except:
                pass
            
        return None

    def draw_card(self, player=None, count=1):
        """Let the player draw a card"""

        for _ in xrange(count):
            (player or self.active_player).draw_card()
        self.update_player(player or self.active_player)

    def update(self):
        """The game's main-loop, called by the server's loop"""

        if self.pending_trigger:
            if self.running_trigger:
                return

            for p in self.pending_trigger.keys():
                if not self.pending_trigger[p]:
                    del self.pending_trigger[p]
                else:
                    triggerinfo = self.pending_trigger[p][0]
                    self.running_trigger = triggerinfo
                    
                    def remove(*args):
                        self.pending_trigger[p].remove(triggerinfo)
                        self.running_trigger = None
                    
                    self.on_resolve(triggerinfo.card, remove)
                    triggerinfo(self, p)
                    return
        
        self.phase.update()

    def check_endcondition(self):
        return game_end(self)

    def end_of_game(self):
        logging.info("game over")

        self.running = False
        result = self.calculate_result()

        GameEndEvent(result).post(self.ev)

    def calculate_result(self):
        for p in self.players:
            for c in p.deck:
                c.end_step(self, p)
        return [(p.name, p.score) for p in self.players]
       
    def _next_player(self):
        """Set the next player as active"""

        print "- next player -----------------------"

        self.action_step_handler = []
        self.buy_step_handler = []

        self._active_player = self.next_player() 
        #logging.debug("----- next player (%s)-------", self.active_player.name)
        self.yell("It's now %ss turn" % self.active_player.name)
        PlayerInfoEvent([p.create_info() for p in self.players]).post(self.ev)

    def previous_player(self):
        """Return the previous player before the actual one"""

        previous_player = (self.players)[self.players.index(self._active_player) - 1]
        return previous_player if not previous_player is self.active_player else None

    def next_player(self, current=None):
        """Return the next player after the actual one"""

        if not current:
            current = self._active_player
        
        next_index = self.players.index(current) + 1
        return (self.players)[0] if next_index == len(self.players) else (self.players)[next_index] 
        
    def endphase(self, player):
        """End the current phase"""

        assert player == self.active_player, \
            "Only active player may end his phase"
        assert self.subphaseinfo.subphase == SP_PLAYERINPUT, \
            "Player has to answer to %s first" % self.subphaseinfo.subphase
        self.phase.next_phase()

    def has_played(self, card_class):
        return any(isinstance(c, card_class) for c in self.last_played_cards[self.active_player])

    def let_all_players_pick(self, card, text, handler=None, player_filter=None):
        self.all_player_action(card, 
                               handler or card.handler, 
                               SP_PICKCARDSFROMHAND, 
                               InfoToken(text), 
                               player_filter)
        
    def ask_all_players(self, card, askplayerinfo, handler=None, player_filter=None):
        self.all_player_action(card, handler or card.handler, 
                               SP_ASKPLAYER, askplayerinfo, player_filter)

    def all_player_action(self, card, handler, subphase, info,
                          player_filter=None):

        if not player_filter:
            player_filter = lambda p: True
        players = [p for p in self.players if player_filter(p)]
        for p in players:
            (self.all_player_action_cache)[p] = handler
            if p is self.active_player:
                self.enter_subphase(SubPhaseInfo(subphase, card, info, handler))
            else:
                ChangeSubPhaseEvent(card.id, p, subphase, info).post(self.ev)

        return players

    def let_pick_pile(self, card, text, callback=None):
        self.enter_subphase(SubPhaseInfo(SP_PICKCARD, 
                                         card,
                                         InfoToken(text),
                                         callback or card.handler))
        
    def let_pick_from_hand(self, card, text, callback=None):
        self.enter_subphase(SubPhaseInfo(SP_PICKCARDSFROMHAND, 
                                         card,
                                         InfoToken(text),
                                         callback or card.handler))

    def attack_ask(self, card, info, attack_handler=None,
               expect_answer=True, on_restore_callback=None):

        self.attack(card, attack_handler or card.attack_handler, SP_ASKPLAYER,
                    info, expect_answer, on_restore_callback)

    def attack_let_pick_from_hand(self, card, text, attack_handler=None,
               expect_answer=True, on_restore_callback=None):
        
        self.attack(card, attack_handler or card.attack_handler, SP_PICKCARDSFROMHAND,
                    InfoToken(text), expect_answer, on_restore_callback)

    def attack(self, card, attack_handler=None, subphase=None, info=None,
               expect_answer=True, on_restore_callback=None, keep_WAIT=False):

        assert card, "card is none"
        attack_handler = attack_handler or card.attack_handler

        def orc_proxy(game, player):
            if on_restore_callback:
                on_restore_callback(game, player)
            self.resolved(card)

        self.enter_subphase(SubPhaseInfo(SP_WAIT, 
                                         card,
                                         InfoToken('Waiting for other players'),
                                         on_restore_callback=orc_proxy))

        attacked_players = [p for p in self.players if p != self.active_player]

        if not attacked_players:
            return

        attack_phase = subphase or SP_WAIT

        
        def add_to_attack_cache_or_resolve():
            if expect_answer:
                (self.attack_cache)[p] = attack_handler
                ChangeSubPhaseEvent(card.id, p, attack_phase, info).post(self.ev)
                return True
            
            # if we don't expect an answer (e.g. the attack cards just says: take a curse)
            # we can just call the 'attack_handler' stored in 'attack_cache', so
            # the attack takes place immediately.
            return attack_handler(self, p, None) != CANCEL_ATTACK
                
        cancel = True        
        for p in attacked_players:
            triggerable_cards ={ t[0]: t[1] for t in [(c, c.handle_trigger(T_ATTACK)) for c in p.hand] if t[1] != None}
           
            reaction_cards = list(set([c.name for c in triggerable_cards.keys()]))

            if reaction_cards:

                def handle_answer(game, player, result):
                    if result == "play no reaction":
                        return add_to_attack_cache_or_resolve
                    else:
                        card = (c for c in player.hand if c.name == result).next()
                        self.yell("%s reveals %s" % (player.name, card.name))
                        
                        result = triggerable_cards[card]
                        if callable(result):
                            def wrapper():
                                result(self, player, add_to_attack_cache_or_resolve)
                            return wrapper    
                        else:
                            ChangeSubPhaseEvent(None, p, SP_WAIT).post(self.ev)
                            
                    return True

                reaction_cards.append("play no reaction")
                q_info = AskPlayerInfo('Attacked by %s' % card.name,
                        "Play reaction card?", reaction_cards, card)
                ChangeSubPhaseEvent(uuid4(), p, SP_ASKPLAYER, q_info).post(self.ev)
                (self.reaction_cache)[p] = handle_answer
            else:
                if add_to_attack_cache_or_resolve():
                    cancel = False
        
        if (not expect_answer and not self.reaction_cache and not keep_WAIT) or cancel:
            self._restore_subphase()

    def ask(self, card, text, answers, callback=None, on_restore_callback=None):
        self.enter_subphase(AskSubPhase(card, 
                                        text, 
                                        answers, 
                                        callback or card.handler, 
                                        on_restore_callback))

    def ask_yes_no(self, card, text, callback=None, on_restore_callback=None, card_to_show=None):
        self.enter_subphase(YesNoSubPhase(card, 
                                          text, 
                                          callback or card.handler,
                                          on_restore_callback, 
                                          card_to_show))

    def let_order_cards(self, card, text, cards, callback):
        for c in cards:
            c.calc_cost = self.get_cost(c)
        self.enter_subphase(SubPhaseInfo(SP_ORDERCARDS, 
                                         card,
                                         InfoToken(text, cards=cards), 
                                         callback=callback))

    def enter_subphase(self, subphaseinfo):
        """
        Enter a subphase and keep it on a stack, so multiple calls gets resolved in right order
        callback: is called when the game receives an answer from a player which is not 
                  in the attack or reaction cache, e.g. after choosing the cards to trash
                  with chapel etc.
        on_restore_callback: is called when the sub phase is restored."""

        assert subphaseinfo, "subphaseinfo is None"

        if not self.subphase_cache:
            self.subphase_cache.append(self.subphaseinfo)

            self.subphaseinfo = subphaseinfo

            ChangeSubPhaseEvent(subphaseinfo.card.id, self.active_player,
                    self.subphaseinfo.subphase, self.subphaseinfo.info).post(self.ev)
        else:
            self.subphase_cache.append(subphaseinfo)

    def _restore_subphase(self):
        """Get back to the last subphase

        The on_restore_callback-handlers are important for attack cards that do something after changing the sub-phase
        to resolve an effect. For example, the Swindler forces each player to reveal the top card of the deck. After
        each player revealed the card, the sub-phase changes back from the attack sub-phase to the previous sub-phase,
        and this is the point in time where the Swindler wants to decide which cards are replaced.
        """

        cb = self.subphaseinfo.on_restore_callback

        self.subphaseinfo = self.subphase_cache.pop()

        ChangeSubPhaseEvent(self.subphaseinfo.card, self.active_player,
                self.subphaseinfo.subphase, info=self.subphaseinfo.info).post(self.ev)

        if cb:
            cb(self, self.active_player)

        for lc in self.late_calls:
            lc()
        self.late_calls = []

    def answered(self, player, result, subid):
        """Handle the given answer"""

        caches = (self.attack_cache, 
                  self.reaction_cache, 
                  self.all_player_action_cache,
                  self.misc_cache)

        handled = False
        
        for cache in caches:
            if not handled and player in cache.keys():
                handled = True
                handler_result = cache[player](self, player, result)

                if handler_result:
                    del cache[player]
                    ChangeSubPhaseEvent(None, player, SP_WAIT).post(self.ev)
                    
                    if isinstance(handler_result, LateCall):
                        self.late_calls.append(handler_result)
                    elif callable(handler_result):
                        handler_result()

                    if not [item for sublist in caches for item in sublist]:
                        self._restore_subphase()

        if not handled and self.subphaseinfo.callback:
            cbresult = self.subphaseinfo.callback(self, player, result)
            if cbresult:
                self._restore_subphase()
                if callable(cbresult):
                    cbresult()

    def resolved(self, card):
        """Called by cards to tell the game they are resolved"""

        if card.id in self.resolve_handler:
            (self.resolve_handler)[card.id](self, self.active_player)
            del (self.resolve_handler)[card.id]

        self.update_player(self.active_player)

    def on_resolve(self, card, f):
        """Register a function that is called when a card tells it is resolved"""

        (self.resolve_handler)[card.id] = f

    def reveal_player_hand(self, player=None):
        player = player or self.active_player
        for c in player.hand:
            self.yell("%s reveals %s" % (player.name, c.name))

    def reveal_top_card(self, player=None):
        player = player or self.active_player
        card = player.draw_card(just_reveal=True)
        if card:
            self.yell("%s reveals %s" % (player.name, card.name))
        else:
            self.yell("%s has no cards left" % player.name)
        return card

    def get_player_by_id(self, player_id):
        return (p for p in self.players if p.id == player_id).next()

    def add_action_step_handler(self, card_class, callback):
        self.action_step_handler.append(StepHandler(card_class, callback))

    def add_buy_step_handler(self, card_class, callback):
        self.buy_step_handler.append(StepHandler(card_class, callback))

    def notify(self, event):
        pass
