#!/usr/bin/python
# -*- coding: utf-8 -*-

from game.cards.card import Card, ACTION, TREASURE
from game.cards.common import Copper


class City(Card):

    cardtype = ACTION
    cost = (5, 0)
    name = "City"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.draw_card()
        player.actions += 2
        num_empty_piles = len([p for p in game.allpiles if len(p) == 0])
        if num_empty_piles >= 1:
            game.draw_card()
        if num_empty_piles >= 2:
            player.money += 1
            player.buys += 1
        game.resolved(self)


class WorkersVillage(Card):

    cardtype = ACTION
    cost = (4, 0)
    name = "Workers Village"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.draw_card()
        player.actions += 2
        player.buys += 1
        game.resolved(self)


class Expand(Card):

    cardtype = ACTION
    cost = (7, 0)
    name = "Expand"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.let_pick_from_hand(self, "Pick a card to trash")

    def handler(self, game, player, result):
        if not player.hand:
            return True
        if len(result) != 1:
            game.whisper("You have to choose one card")
            return False

        card = player.hand.get_card(result[0])
        card_cost = game.get_cost(card)

        def pick_handler(game, player, result):
            pile = (p for p in game.allpiles if p.id == result).next()
            if game.get_cost(pile)[0] > card_cost[0] + 3 or (pile.cost)[1] > \
                card_cost[1]:
                game.whisper("You have to pick a card with cost up to %i/%i" %
                             (card_cost[0] + 3, card_cost[1]))
                return False
            game.take_card_from_pile(player, pile)
            game.resolved(self)
            return True

        game.trash_card(player, card)

        game.let_pick_pile(self, "Pick a card costing up to %i/%i" % (card_cost[0] +
                            3, card_cost[1]), pick_handler)
        
        return True


class Bank(Card):

    cardtype = TREASURE
    cost = (7, 0)
    name = "Bank"

    def __init__(self):
        Card.__init__(self)

    def buy_step(self, game, player):
        treasures = (c for c in game.last_played_cards[player] if c.cardtype & TREASURE)
        player.money += sum(1 for _ in treasures) + 1
       
        game.resolved(self)

    def action_step(self, game, player):
        self.buy_step(game, player)


class CountingHouse(Card):

    cardtype = ACTION
    cost = (5, 0)
    name = "Counting House"
    
    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        
        coppers = player.discardpile.get_all_of_card_class(Copper)
        
        def take(game, player, result):
            for card_id in result:
                card = player.deck.get_card(card_id)
                player.discardpile.remove(card)
                player.hand.add(card)
            game.resolved(self)
            return True
            
        if coppers:
            game.let_order_cards(self, 'Choose any number of Copper to put on your hand', coppers, take)
        else:
            game.resolved(self)
