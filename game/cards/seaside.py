#!/usr/bin/python
# -*- coding: utf-8 -*-

from game.cards.card import Card, ACTION, ATTACK, DURATION, VICTORY
from game.cards.common import Curse, Copper, Gold


class Ghostship(Card):

    cardtype = ACTION | ATTACK
    cost = (5, 0)
    name = "Ghostship"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.draw_card(count=2)

        game.attack_let_pick_from_hand(self, 'Discard down to three cards')

    def attack_handler(self, game, attacked_player, result):
        if len(attacked_player.hand) < 4:
            return True
        toputback = max(0, len(attacked_player.hand) - 3)
        if len(result) != toputback:
            game.whisper("You have to choose %s cards" % toputback, attacked_player)
            return False
        put_back = [card for card in attacked_player.hand if card.id in
                    result]
        for card in put_back:
            attacked_player.move_card_to_pile(card, attacked_player.drawpile)
        game.update_player(attacked_player)
        return True


class Wharf(Card):

    cardtype = ACTION | DURATION
    cost = (5, 0)
    name = "Wharf"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.draw_card(count=2)
        player.buys += 1
        game.resolved(self)

    def begin_step(self, game, player):
        self.action_step(game, player)


class Seahag(Card):

    cardtype = ACTION | ATTACK
    cost = (4, 0)
    name = "Seahag"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.attack(self, self.attack_handler, expect_answer=False)

    def attack_handler(self, game, attacked_player, result):
        card = game.reveal_top_card(attacked_player)
        if card:
            attacked_player.move_card_to_pile(card, attacked_player.discardpile)
        curse_pile = game.get_pile(Curse)
        curse = curse_pile.take(save=True)
        if curse:
            attacked_player.put_on_drawpile(curse)
            game.yell('%s puts a Curse on top of the deck' %
                      attacked_player.name)

        game.update_player(attacked_player)
        return True


class Caravan(Card):

    cardtype = ACTION | DURATION
    cost = (4, 0)
    name = "Caravan"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.draw_card()
        player.actions += 1
        game.resolved(self)

    def begin_step(self, game, player):
        game.draw_card()


class Salvager(Card):

    cardtype = ACTION
    cost = (4, 0)
    name = "Salvager"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.buys += 1
        game.let_pick_from_hand(self, 'Pick a card to salvage')

    def handler(self, game, player, result):
        if not player.hand:
            return True
        if len(result) != 1:
            game.whisper("You have to choose one card")
            return False
        card = (card for card in player.hand if card.id in result).next()
        player.money += game.get_cost(card)[0]
        game.trash_card(player, card)
        game.resolved(self)
        return True


class Bazaar(Card):

    cardtype = ACTION
    cost = (5, 0)
    name = "Bazaar"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.draw_card()
        player.actions += 2
        player.money += 1
        game.resolved(self)


class MerchantShip(Card):

    cardtype = ACTION | DURATION
    cost = (5, 0)
    name = "Merchant Ship"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.money += 2
        game.resolved(self)

    def begin_step(self, game, player):
        self.action_step(game, player)


class PearlDiver(Card):

    cardtype = ACTION
    cost = (2, 0)
    name = "Pearl Diver"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.draw_card()
        player.actions += 1
        if not player.drawpile:
            player.discardpile.shuffle_into(player.drawpile)
        if player.drawpile:
            bottom_card = player.drawpile.bottom_card
            game.ask_yes_no(self, 'Put %s on top of your deck?' % bottom_card.name.replace("_", " "))
        else:
            game.resolved(self)

    def handler(self, game, player, result):
        if result == 'Yes':
            bottom_card = player.drawpile.bottom_card
            player.drawpile.remove(bottom_card)
            player.drawpile.add(bottom_card)
        game.resolved(self)
        return True


class Cutpurse(Card):

    cardtype = ACTION | ATTACK
    cost = (4, 0)
    name = "Cutpurse"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.money += 2
        game.attack(self, self.attack_handler, expect_answer=False)

    def attack_handler(self, game, attacked_player, result):

        coppers = attacked_player.hand.get_all_of_card_class(Copper)

        if coppers:
            game.discard_card(attacked_player, coppers[0])
        else:
            game.reveal_player_hand(attacked_player)

        game.update_player(attacked_player)
        return True


class Smugglers(Card):

    cardtype = ACTION
    cost = (4, 0)
    name = "Smugglers"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        prev_player = game.previous_player()
        if not prev_player:
            game.resolved(self)
            return True

        possible_cards = set([c.name for c in (game.last_gained_cards)[prev_player]
                             if game.get_cost(c)[0] <= 6 and (c.cost)[1] ==
                             0 and game.get_pile(c.__class__)])
        if not possible_cards:
            game.whisper("Can't take any card with Smugglers")
            game.resolved(self)
            return True

        if len(possible_cards) == 1:
            game.take_card_from_pile(player, game.get_pile(list(possible_cards)[0]))
            game.resolved(self)
            return True

        game.ask(self, 'Take which card?', possible_cards)

    def handler(self, game, player, result):
        game.take_card_from_pile(player, game.get_pile(result))
        game.resolved(self)
        return True


class Warehouse(Card):

    cardtype = ACTION
    cost = (3, 0)
    name = "Warehouse"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.draw_card(count=3)
        player.actions += 1
        game.let_pick_from_hand(self, 'Discard 3 cards')

    def handler(self, game, player, result):
        if len(result) != 3 and not (len(result) < 3 and len(result) ==
                len(player.hand)):
            game.whisper("You have to choose three cards")
            return False
        
        for card_id in result:
            card = (card for card in player.hand if card.id == card_id).next()
            game.discard_card(player, card)
        game.resolved(self)
        return True


class Tactician(Card):

    cardtype = ACTION | DURATION
    cost = (5, 0)
    name = "Tactician"

    def __init__(self):
        Card.__init__(self)
        self.any_cards = False

    def action_step(self, game, player):
        self.any_cards = game.discard_hand(player)
        game.resolved(self)

    def begin_step(self, game, player):
        if self.any_cards:
            game.draw_card(count=5)
            player.buys += 1
            player.actions += 1
        game.resolved(self)


class Haven(Card):

    cardtype = ACTION | DURATION
    cost = (2, 0)
    name = "Haven"

    def __init__(self):
        Card.__init__(self)
        self.card = None

    def action_step(self, game, player):
        self.card = None
        game.draw_card()
        player.actions += 1
        if player.hand:
            game.let_pick_from_hand(self, "Pick a card to set aside")

    def handler(self, game, player, result):
        if len(result) != 1:
            game.whisper("You have to choose one card")
            return False

        card = (c for c in player.hand if c.id in result).next()
        self.card = card
        player.hand.remove(card)
        game.yell("%s sets aside a card" % player.name)
        game.update_player(player)
        return True

    def begin_step(self, game, player):
        game.yell("%s puts a card in his hand from haven" % player.name)
        player.hand.add(self.card)
        game.update_player(player)


class TreasureMap(Card):

    cardtype = ACTION
    cost = (4, 0)
    name = "Treasure Map"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        ts = [card for card in player.hand if isinstance(card,
              TreasureMap)]
        if len(ts):
            game.trash_card(player, self)
            game.trash_card(player, ts[0])
            goldpile = game.get_pile(Gold)
            for _ in xrange(4):
                game.take_card_from_pile(player, goldpile, safe=True,
                        to_deck=True)
            game.resolved(self)


class Treasury(Card):

    cardtype = ACTION
    cost = (5, 0)
    name = "Treasury"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.draw_card()
        player.actions += 1
        player.money += 1

    def cleanup_step(self, game, player):
        bought_victories = [c for c in (game.last_bought_cards)[player]
                            if c.cardtype & VICTORY]
        if not bought_victories:
            game.ask_yes_no(self, 'Put Treasury on top of your deck?')

    def handler(self, game, player, result):
        if result == 'Yes':
            player.board.remove(self)
            player.drawpile.add(self)
            game.yell("%s puts Treasury on top of his deck" % player.name)
        game.resolved(self)
        return True


class FishingVillage(Card):

    cardtype = ACTION | DURATION
    cost = (3, 0)
    name = "Fishing Village"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.actions += 2
        player.money += 1
        game.resolved(self)

    def begin_step(self, game, player):
        player.actions += 1
        player.money += 1


