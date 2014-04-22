#!/usr/bin/python
# -*- coding: utf-8 -*-

from game.cards.card import Card, ACTION, VICTORY, ATTACK, TREASURE
from game.cards.common import Curse, Duchy, Gold

#TODO golem/possesion

class Philosophersstone(Card):
    
    cardtype = TREASURE
    cost = (3, 1)
    name = "Philosopher's Stone"
    
    def buy_step(self, game, player):
        dis = len(player.discardpile)
        deck = len(player.drawpile)
        player.money += abs(dis-deck) / 5
    

class Alchemist(Card):

    cardtype = ACTION
    cost = (3, 1)
    name = "Alchemist"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.draw_card(count=2)
        player.actions += 1

    def cleanup_step(self, game, player):
        potions = [c for c in player.board if c.name == "Potion"]
        if potions:
            game.ask_yes_no(self, 'Put Alchemist on top of your deck?')

    def handler(self, game, player, result):
        if result == 'Yes':
            player.board.remove(self)
            player.drawpile.add(self)
            game.yell("%s puts Alchemist on top of his deck" %
                      player.name)
        game.resolved(self)
        return True
            
            
class ScryingPool(Card):

    cardtype = ACTION | ATTACK
    cost = (2, 1)
    name = "Scrying Pool"

    def __init__(self):
        Card.__init__(self)
        self.revealed = {}

    def action_step(self, game, player):
        self.revealed = {}
        player.actions += 1
        (self.revealed)[player.id] = game.reveal_top_card(player)

        game.attack(self, self.attack_handler, expect_answer=False,
                    on_restore_callback=self.handler)

    def attack_handler(self, game, attacked_player, result):
        (self.revealed)[attacked_player.id] = game.reveal_top_card(attacked_player)
        return True

    def handler(self, game, player):
        gen = [(game.get_player_by_id(pid), (self.revealed)[pid]) for pid in
               self.revealed if (self.revealed)[pid]]

        def do_scry(*args, **kwargs):
            try:
                (p, card) = gen.pop()

                def handle_answer(_, ap, result):
                    if result == 'Yes':
                        ap.discardpile.add(card)
                    else:
                        ap.drawpile.add(card)
                    return True

                game.ask_yes_no(self, "Discard %s's %s?" % (p.name, card.name),
                                handle_answer, do_scry, card)
            except IndexError:
                
                revealed = []
                def put_on_hand():
                    for card in revealed:
                        player.hand.add(card)
                        game.update_player(game.active_player)
                    return True
                
                while 1:
                    card = game.reveal_top_card()
                    if not card:
                        return put_on_hand()
                    revealed.append(card)
                    if not card.cardtype & ACTION:
                        return put_on_hand()
                
        do_scry()
        

class Herbalist(Card):

    cardtype = ACTION
    cost = (2, 0)
    name = "Herbalist"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.buys += 1
        player.money += 1

    def cleanup_step(self, game, player):
        treasures = [c for c in player.board if c.cardtype & TREASURE]
        
        def put_back(game, player, result):
            if len(result) > 1:
                game.whisper("You have to choose one or zero cards")
                return False
                
            for card_id in result:
                card = player.deck.get_card(card_id)
                player.put_on_drawpile(card)
            game.resolved(self)
            return True
            
        if treasures:
            game.let_order_cards(self, 'Put up to one Treasure back on your deck', treasures, put_back)
        else:
            game.resolved(self)

    
class Vineyard(Card):

    cardtype = VICTORY
    cost = (0, 1)
    name = "Vineyard"

    def __init__(self):
        Card.__init__(self)

    def end_step(self, game, player):
        action_cards = player.deck.get_actions()
        player.score += len(action_cards) / 3


class Familiar(Card):

    cardtype = ACTION | ATTACK
    cost = (3, 1)
    name = "Familiar"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.draw_card()
        player.actions += 1

        game.attack(self, expect_answer=False)

    def attack_handler(self, game, attacked_player, result):
        curse_pile = game.get_pile(Curse)
        game.take_card_from_pile(attacked_player, curse_pile, safe=True)
        return True


class University(Card):

    cardtype = ACTION
    cost = (2, 1)
    name = "University"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.actions += 2
        game.ask_yes_no(self, 'Gain an Action card costing up to 5?')

    def handler(self, game, player, result):
        if result == 'Yes':
            game.let_pick_pile(self, "Pick an Action card costing up to 5", self.pick_handler)
        else:
            game.resolved(self)
        game.update_player(player)
        return True

    def pick_handler(self, game, player, result):
        pile = next(pile for pile in game.allpiles if pile.id == result)
        if game.get_cost(pile)[0] > 5 or (pile.cost)[1] > 0 or not pile.card.cardtype & \
            ACTION:
            game.whisper("You have to pick an Action card with cost up to 5")
            return False
        game.take_card_from_pile(player, pile)
        game.resolved(self)
        return True


class Transmute(Card):

    cardtype = ACTION
    cost = (0, 1)
    name = "Transmute"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.let_pick_from_hand(self, 'Pick a card to trash')

    def handler(self, game, player, result):
        if not player.hand:
            return True
        if len(result) != 1:
            game.whisper("You have to choose one card")
            return False
        card = next(card for card in player.hand if card.id in result)
        game.trash_card(player, card)
        if card.cardtype & ACTION:
            game.take_card_from_pile(player, game.get_pile(Duchy), safe=
                    True)
        if card.cardtype & TREASURE:
            game.take_card_from_pile(player, game.get_pile(Transmute),
                    safe=True)
        if card.cardtype & VICTORY:
            game.take_card_from_pile(player, game.get_pile(Gold), safe=
                    True)
        game.resolved(self)
        return True


class Apprentice(Card):

    cardtype = ACTION
    cost = (5, 0)
    name = "Apprentice"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.actions += 1
        game.let_pick_from_hand(self, 'Pick a card to trash')

    def handler(self, game, player, result):
        if not player.hand:
            return True
        if len(result) != 1:
            game.whisper("You have to choose one card")
            return False
        card = next(card for card in player.hand if card.id in result)
        [game.draw_card() for _ in xrange(game.get_cost(card)[0])]
        game.trash_card(player, card)
        if (card.cost)[1]:
            game.draw_card(count=2)
        game.resolved(self)
        return True


class Apothecary(Card):

    cardtype = ACTION
    cost = (2, 1)
    name = "Apothecary"
    
    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.actions += 1
        game.draw_card()
        self.handler(game, player)

    def handler(self, game, player):

        cards = []
        for _ in xrange(4):
            card = game.reveal_top_card(player)
            if card:
                if card.name in ("Copper", "Potion"):
                    player.hand.add(card)
                else:
                    cards.append(card)

        def put_back(game, player, result):
            if len(result) != len(cards):
                game.whisper("You have to choose all cards")
                return False
                
            for card_id in result:
                card = player.deck.get_card(card_id)
                player.put_on_drawpile(card)
            game.resolved(self)
            return True
            
        if cards:
            game.let_order_cards(self, 'Put cards back on your deck', cards, put_back)
        else:
            game.resolved(self)


