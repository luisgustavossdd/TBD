#!/usr/bin/python
# -*- coding: utf-8 -*-

from game.cards.card import Card, ACTION, TREASURE, REACTION
from game.cards.common import Silver, Province, Gold
from game.cards.common import Copper, Curse
from game.gametrigger import T_GAIN
from game.gamestates import SP_ASKPLAYER, SP_WAIT
from game.askplayerinfo import AskYesNo
from game.subphaseinfo import SubPhaseInfo
from framework.event import ChangeSubPhaseEvent


class Embassy(Card):

    cardtype = ACTION
    cost = (5, 0)
    name = "Embassy"

    def __init__(self):
        Card.__init__(self)

    def gain_step(self, game, player):
        silver = game.get_pile(Silver)
        for p in game.other_players:
            game.take_card_from_pile(p, silver, safe=True)

    def action_step(self, game, player):
        game.draw_card(count=5)
        game.let_pick_from_hand(self, 'Discard 3 cards')

    def handler(self, game, player, result):
        if len(result) != 3:
            game.whisper("You have to choose three cards")
            return False
        game.discard_cards(result)
        game.resolved(self)
        return True


class IllGottenGains(Card):

    cardtype = TREASURE
    cost = (5, 0)
    name = 'Ill-Gotten Gains'

    def __init__(self):
        Card.__init__(self)

    def buy_step(self, game, player):
        player.money += 1
        game.ask_yes_no(self, 'Put a Copper into your Hand?')

    def action_step(self, game, player):
        self.buy_step(game, player)

    def gain_step(self, game, player):
        curse = game.get_pile(Curse)
        for p in game.other_players:
            game.take_card_from_pile(p, curse, safe=True)       
        
    def handler(self, game, player, result):
        if result == 'Yes':
            game.take_card_from_pile(player, game.get_pile(Copper), to_hand=True)
        game.update_player(player)
        game.resolved(self)
        return True


class Oasis(Card):

    cardtype = ACTION
    cost = (3, 0)
    name = "Oasis"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.draw_card()
        player.actions += 1
        player.money += 1
        game.let_pick_from_hand(self, 'Discard one card')

    def handler(self, game, player, result):
        if len(result) != 1:
            game.whisper("You have to choose one cards")
            return False
        game.discard_cards(result)
        game.resolved(self)
        return True


class Crossroads(Card):

    cardtype = ACTION
    cost = (2, 0)
    name = "Crossroads"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.reveal_player_hand()
        game.draw_card(count=len(player.hand.get_victories()))

        if not game.has_played(Crossroads):
            player.actions += 3

        game.resolved(self)


class NomadCamp(Card):

    cardtype = ACTION
    cost = (4, 0)
    name = "Nomad Camp"

    def __init__(self):
        Card.__init__(self)

    def gain_step(self, game, player):
        player.move_card_to_pile(self, player.drawpile)

    def action_step(self, game, player):
        player.buys += 1
        player.money += 2
        game.resolved(self)


class Cache(Card):

    cardtype = TREASURE
    cost = (5, 0)
    name = "Cache"

    def __init__(self):
        Card.__init__(self)

    def gain_step(self, game, player):
        for _ in xrange(2):
            game.take_card_from_pile(player, game.get_pile(Copper))

    def buy_step(self, game, player):
        player.money += 3

    def action_step(self, game, player):
        self.buy_step(game, player)


class FoolsGold(Card):

    cardtype = TREASURE | REACTION
    cost = (2, 0)
    name = "Fool's Gold"
    
    def __init__(self):
        Card.__init__(self)
            
    def buy_step(self, game, player):
        player.money += 4 if game.has_played(FoolsGold) else 1
        
    def action_step(self, game, player):
        self.buy_step(game, player)    
        
    def handle_trigger(self, trigger):
        if trigger == T_GAIN:
            return self.trigger_callback
            
    def trigger_callback(self, game, player, causer_player, causer_card):
        if not player is causer_player and isinstance(causer_card, Province):
            game.enter_subphase(SubPhaseInfo(SP_WAIT, self))
            ChangeSubPhaseEvent(self.id, 
                                player, 
                                SP_ASKPLAYER, 
                                AskYesNo(self, "Trash for Gold?")).post(game.ev)
            (game.misc_cache)[player] = self.trash_handler
        else:
            game.resolved(self)
    
    def trash_handler(self, game, player, result): 
        if result == "Yes":
            game.trash_card(player, self)
            gold = game.get_pile(Gold)
            game.take_card_from_pile(player, gold, to_deck=True)
        game.resolved(self)
        return True
            
        
        
             
        
        