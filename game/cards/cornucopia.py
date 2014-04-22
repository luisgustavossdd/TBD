#!/usr/bin/python
# -*- coding: utf-8 -*-

from game.cards.card import Card, ACTION, ATTACK, TREASURE, VICTORY
from game.askplayerinfo import AskYesNo
from framework.latecall import LateCall
from game.cards.common import Curse, Estate, Gold, Silver


class Harvest(Card):

    cardtype = ACTION
    cost = (5, 0)
    name = "Harvest"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        names = set()
        for _ in xrange(4):
            card = player.draw_card(just_reveal=True)
            if card:
                game.yell("%s reveals and discards %s" % (player.name,
                          card.name))
                player.discardpile.add(card)
                names.add(card.name)
        player.money += len(names)
        game.resolved(self)


class BagOfGold(Card):

    cardtype = ACTION
    cost = (0, 0)
    name = "Bag of Gold"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.actions += 1
        game.take_card_from_pile(player, game.get_pile(Gold), safe=True,
                                 to_deck=True)
        game.resolved(self)


class Fairgrounds(Card):

    cardtype = VICTORY
    cost = (6, 0)
    name = "Fairgrounds"

    def __init__(self):
        Card.__init__(self)

    def end_step(self, game, player):
        names = set()
        for c in player.deck:
            names.add(c.name)

        player.score += (len(names) / 5) * 2


class TrustySteed(Card):

    cardtype = ACTION
    cost = (0, 0)
    name = "Trusty Steed"

    def __init__(self):
        Card.__init__(self)
        self.actions_list = ("+2 cards", "+2 actions", "+2",
                             "4 Silvers, discard deck")

    def action_step(self, game, player):
        game.ask(self, 'Choose one:', self.actions_list)

    def do_steed(self, game, player, result):
        if result == "+2 cards":
            game.draw_card(count=2)
        elif result == "+2 actions":
            player.actions += 2
        elif result == "+2":
            player.money += 2
        else:
            for _ in xrange(4):
                game.take_card_from_pile(player, game.get_pile(Silver),
                        safe=True)
            [player.discardpile.add(player.drawpile.take()) for _ in
             xrange(len(player.drawpile))]
            game.update_player(player)

    def handler(self, game, player, result):
        self.do_steed(game, player, result)

        game.ask(self, 'Choose one:', [i for i in self.actions_list if i !=
                 result], self.second_handler)

        return True

    def second_handler(self, game, player, result):
        self.do_steed(game, player, result)
        game.resolved(self)
        return True


class Followers(Card):

    cardtype = ACTION | ATTACK
    cost = (0, 0)
    name = "Followers"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.draw_card(count=2)

        game.take_card_from_pile(player, game.get_pile(Estate), safe=
                                 True)

        game.attack_let_pick_from_hand(self, "Discard down to three cards")

    def attack_handler(self, game, attacked_player, result):
        todis = max(0, len(attacked_player.hand) - 3)
        if len(result) != todis:
            game.whisper(attacked_player, "You have to choose %s cards" %
                         todis)
            return False
        discard = [card for card in attacked_player.hand if card.id in
                   result]
        [game.discard_card(attacked_player, card) for card in discard]
        game.take_card_from_pile(attacked_player, game.get_pile(Curse),
                                 safe=True)
        return True


class Diadem(Card):

    cardtype = TREASURE
    cost = (0, 0)
    name = 'Diadem'

    def __init__(self):
        Card.__init__(self)

    def buy_step(self, game, player):
        player.money += 2
        player.money += player.actions

    def action_step(self, game, player):
        self.buy_step(game, player)


class HuntingParty(Card):

    cardtype = ACTION
    cost = (5, 0)
    name = "Hunting Party"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.draw_card()
        player.actions += 1

        game.reveal_player_hand(player)

        def is_in_hand(card):
            return [c for c in player.hand if c.name == card.name]

        max_draws = len(player.drawpile) + len(player.discardpile)
        revealed_list = []
        while len(revealed_list) < max_draws:
            revealed = game.reveal_top_card(player)
            if not revealed:
                break
            if not is_in_hand(revealed):
                game.yell("%s puts %s into his hand" % (player.name,
                          revealed.name))
                player.hand.add(revealed)
                break

            revealed_list.append(revealed)

        for c in revealed_list:
            player.discardpile.add(c)

        game.resolved(self)


class Princess(Card):

    cardtype = ACTION
    cost = (0, 0)
    name = "Princess"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.buys += 1

        def mod(coins, potions):
            if self in player.board:
                return (coins - 2, potions)

        game.add_cost_mod(mod)

        game.resolved(self)


class Tournament(Card):

    cardtype = ACTION
    cost = (4, 0)
    name = "Tournament"

    prices = [BagOfGold, Diadem, Followers, Princess, TrustySteed]

    def __init__(self):
        Card.__init__(self)
        self.pending = 0
        self.province_discarded = False
        self.other_revealed = False

    def action_step(self, game, player):
        self.pending = 0
        self.province_discarded = False
        self.other_revealed = False

        player.actions += 1
        
        player_filter=lambda p: [c for c in p.hand if c.name == "Province"]
        p = game.ask_all_players(self, AskYesNo(self, 'Reveal Province?'),
                                   player_filter=player_filter)

        self.pending = len(p)

    def handler(self, game, player, result):
        if result == "Yes":
            game.yell("%s reveals a Province" % player.name)
            if player is game.active_player:
                game.discard_card(player, (c for c in player.hand if c.name ==
                                  "Province").next())
                self.province_discarded = True
            else:
                self.other_revealed = True

        self.pending -= 1

        if player is game.active_player:
            if self.pending:
                return LateCall(lambda p=player, g=game: self.price_handler(g,
                                p))
            else:
                self.price_handler(game, player)

        return True

    def price_handler(self, game, player):
        if self.province_discarded:

            if not self.other_revealed:
                game.draw_card()
                game.active_player.money += 1

            if len(Tournament.prices):
                prices = [p.name for p in Tournament.prices]
                game.ask(self, 'Pick a Price', prices, self.get_price_handler)
        else:
            game.resolved(self)

    def get_price_handler(self, game, player, result):
        price = (p for p in Tournament.prices if p.name == result).next()
        Tournament.prices.remove(price)
        game.take_card(player, price())
        game.resolved(self)
        return True

    def end_step(self, game, player):
        Tournament.prices = [BagOfGold, Diadem, Followers, Princess,
                             TrustySteed]


