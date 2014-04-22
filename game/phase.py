#!/usr/bin/python
# -*- coding: utf-8 -*-

from gamestates import *
from framework.logger import logcall

class PhaseManager(object):

    """Handles entering/leaving of game phases"""

    def __init__(self, game, phases, enter_callback, entered_callback,
                 end_callback):
        self.__game = game
        self.__phases = phases
        self.__enter_callback = enter_callback
        self.__entered_callback = entered_callback
        self.__end_callback = end_callback
        self.__current_phase = None

    @property
    def current_phase(self):
        return self.__current_phase

    def __eq__(self, other):
        return self.__current_phase.key == other

    def update(self):
        self.__current_phase.update()

    def next_phase(self):
        """Switch to the next phase. If the current phase is the last one, go to the first"""

        if not self.__current_phase:

            self.__current_phase = (self.__phases)[0]
        else:

            self.__end_callback(self.__current_phase)
            self.__current_phase.end()

            try:
                self.__current_phase = (self.__phases)[self.__phases.index(self.__current_phase) + 1]
            except IndexError:
                self.__current_phase = (self.__phases)[0]

        self.__enter_callback(self.__current_phase)
        self.__current_phase.enter()
        self.__entered_callback(self.__current_phase)
        
class Phase(object):

    """A phase of the game."""

    def __init__(self, game):
        self.game = game

    def __getattr__(self, name):
        return getattr(self.game, name)
    
    def enter(self):
        """Called when entering this phase"""

        raise NotImplementedError

    def update(self):
        pass

    def end(self):
        if self.game.check_endcondition():
            self.game.end_of_game()


class ActionPhase(Phase):

    name = "Action phase"
    key = P_ACTION

    def enter(self):

        player = self.game.active_player
        for card in (player.durations.cards)[:]:
            player.durations.remove(card)
            player.hand.add(card)
            self.game.play_card(player, card.id, free=True, is_duration=True)


    def update(self):
        if self.subphaseinfo.subphase == SP_PLAYERINPUT:
            if not self.active_player.can_do_action():
                self.phase.next_phase()

class BuyPhase(Phase):

    name = "Buy phase"
    key = P_BUY

    def enter(self):
        pass
    
    def update(self):
        if self.subphaseinfo.subphase == SP_PLAYERINPUT:
            if self.active_player.buys == 0:
                self.phase.next_phase()

class PreCleanupPhase(Phase):

    name = "Pre-Cleanup phase"
    key = P_PRECLEANUP

    def enter(self):
        pass

    def update(self):
        if self.subphaseinfo.subphase != SP_PLAYERINPUT:
            return
        while self.precleanupstack:
            phase = self.subphaseinfo.subphase
            card = self.precleanupstack.pop()
            card.cleanup_step(self, self._active_player)
            if phase != self.subphaseinfo.subphase:
                return
        self.phase.next_phase()

class CleanupPhase(Phase):

    name = "Cleanup phase"
    key = P_CLEANUP

    def enter(self):
        player = self.game.active_player

        player.potion = 0
        player.money = 0
        player.buys = 1
        player.actions = 1

        played_cards = [player.board.take() for _ in xrange(len(player.board))]
        to_discard = [card for card in played_cards if not card in player.durations]
        for card in to_discard:
            player.discardpile.add(card)

        hand = [player.hand.take() for card in xrange(len(player.hand))]
        for card in hand:
            player.discardpile.add(card)

        for _ in xrange(5):
            player.draw_card()

        self.game.cost_mod = []
        self.game.update_player(player)
        self.game._next_player()
        self.game.phase.next_phase()
