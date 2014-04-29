#!/usr/bin/python
# -*- coding: utf-8 -*-

from functools import partial

from game.cards.card import Card, ACTION, VICTORY, TREASURE, ATTACK, REACTION
from framework.latecall import LateCall
from game.subphaseinfo import SubPhaseInfo
from game.cards.common import Duchy, Silver, Copper, Estate, Curse
from game.askplayerinfo import AskPlayerInfo
from game.gamestates import SP_PICKCARDSFROMHAND, SP_PICKCARD, CANCEL_ATTACK
from game.gametrigger import T_ATTACK
from game.infotoken import InfoToken
from framework.event import ChangeSubPhaseEvent

class WishingWell(Card):
        
    cardtype = ACTION
    cost = (3, 0)
    name = "Wishing Well"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.draw_card()
        player.actions += 1

        answers = set([c.name for c in player.deck])
        game.ask(self, "Name a card", answers)
    
    def handler(self, game, player, result):
        card = game.reveal_top_card()
        player.drawpile.add(card)
        if card.name == result:
            game.draw_card()
        game.resolved(self)
        return True
    
class Swindler(Card):

    cardtype = ACTION | ATTACK
    cost = (3, 0)
    name = "Swindler"

    def __init__(self):
        Card.__init__(self)
        self.revealed = {}

    def action_step(self, game, player):
        self.revealed = {}
        player.money += 2

        game.attack(self, self.attack_handler, expect_answer=False,
                    on_restore_callback=self.handler)

    def attack_handler(self, game, attacked_player, result):
        (self.revealed)[attacked_player.id] = game.reveal_top_card(attacked_player)
        return True

    def handler(self, game, player):
        gen = [(game.get_player_by_id(pid), (self.revealed)[pid]) for pid in
               self.revealed if (self.revealed)[pid]]

        def do_swindler(*args, **kwargs):
            try:
                (p, card) = gen.pop()

                def handle_answer(attacked_player,_, ap, result):
                    game.take_card_from_pile(attacked_player, game.get_pile(result))
                    return True

                game.trash_card(p, card)
                possible_piles = [pi for pi in game.allpiles if pi and game.get_cost(pi) == game.get_cost(card)]
                if not possible_piles:
                    do_swindler()
                else:
                    if len(possible_piles) == 1:
                        game.take_card_from_pile(p, possible_piles[0])
                        do_swindler()
                    else:
                        game.ask(self, "Pick a card for %s" % (p.name), [pi.name for pi in possible_piles], partial(handle_answer, p)) 

            except IndexError:
                return True

        do_swindler()

class SecretChamber(Card):

    cardtype = ACTION | REACTION
    cost = (2, 0)
    name = "Secret Chamber"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.let_pick_from_hand(self, "Discard any number of cards")
        
    def handler(self, game, player, result):
        game.discard_cards(result)
        player.money += len(result)
        game.resolved(self)
        return True

    def handle_trigger(self, trigger):
        if trigger == T_ATTACK:
            return self.trigger_callback
            
    def trigger_callback(self, game, player, attack_func):
        for _ in xrange(2):
            game.draw_card(player)
            ChangeSubPhaseEvent(self.id, 
                                player, 
                                SP_PICKCARDSFROMHAND, 
                                InfoToken("Select two cards to put on deck")).post(game.ev)
        def w(g, p, r):
            if self.discard_handler(g, p, r):
                attack_func()
                return True
        (game.attack_cache)[player] = w
    
    def discard_handler(self, game, player, result):
        if len(result) != 2:
            game.whisper("You have to choose 2 cards")
            return False
        for card_id in result:
            card = player.hand.get_card(card_id)
            player.hand.remove(card)
            player.drawpile.add(card)
        game.update_player()
        return True
    
class Nobles(Card):

    cardtype = ACTION | VICTORY
    cost = (6, 0)
    name = "Nobles"

    def __init__(self):
        Card.__init__(self)

    def end_step(self, game, player):
        player.score += 2

    def action_step(self, game, player):
        game.ask(self, 'Choose one:', ('+3 Cards', '+2 Actions'))

    def handler(self, game, player, result):
        if result == '+3 Cards':
            game.draw_card(count=3)
        else:
            player.actions += 2
        game.resolved(self)
        return True


class Baron(Card):

    cardtype = ACTION
    cost = (4, 0)
    name = "Baron"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.buys += 1
        if [c for c in player.hand if isinstance(c, Estate)]:
            game.ask_yes_no(self, 'Discard Estate?')
        else:
            game.take_card_from_pile(player, game.get_pile(Estate), safe=
                    True)

    def handler(self, game, player, result):
        if result == 'Yes':
            estate = (c for c in player.hand if isinstance(c, Estate)).next()
            game.discard_card(player, estate)
            player.money += 4
        else:
            game.take_card_from_pile(player, game.get_pile(Estate), safe=
                    True)

        game.resolved(self)
        return True

class Saboteur(Card):

    cardtype = ACTION | ATTACK
    cost = (5, 0)
    name = "Saboteur"

    def __init__(self):
        Card.__init__(self)
        self.trashed={}
        
    def action_step(self, game, player):
        self.trashed={}
        game.attack(self, expect_answer=False, keep_WAIT=True)
        
    def attack_handler(self, game, attacked_player, result):
        def discard():
            for c in revealed:
                attacked_player.discardpile.add(c)
            # if there are no players that could destroy cards,
            # don't let the active player wait for nothing
            game.yell("No card to destroy")
            return True if self.trashed else CANCEL_ATTACK
            
        revealed  = []
        while True:
            card = game.reveal_top_card(attacked_player)
            if not card:
                return discard()
            if game.get_cost(card)[0] > 3:
                break
            else:
                revealed.append(card)
                
        game.trash_card(attacked_player, card)
        cost = max(0, game.get_cost(card)[0]-2), card.cost[1]
        self.trashed[attacked_player.id] = cost
        ChangeSubPhaseEvent(self.id, 
                            attacked_player,
                            SP_PICKCARD, 
                            InfoToken("Pick a card costing up to %i or none" % cost[0])).post(game.ev)
        (game.attack_cache)[attacked_player] = self.pick_handler
                
    def pick_handler(self, game, attacked_player, result):
        if not result:
            return True
        pile = game.get_pile(result)
        if pile:
            pile_cost = game.get_cost(pile)
            max_cost = self.trashed[attacked_player.id]
            if pile_cost[0] > max_cost[0] or pile_cost[1] > max_cost[1]: 
                game.whisper("You have to choose a card with cost %i/%i" % (max_cost[0], max_cost[1]),
                             attacked_player)
                return False
            #TODO: check if pile has cards left
            game.take_card_from_pile(attacked_player, pile)
        return True

        
class Torturer(Card):
    
    known = True
    extra_cards= 3

    cardtype = ACTION | ATTACK
    cost = (5, 0)
    name = "Torturer"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.draw_card(count=3)
        game.attack_ask(self, AskPlayerInfo("Torturer",
                                            'Choose one:',
                                            ('Discard 2 cards', 'Take a Curse card on hand'),
                                            self))

    def handler(self, game, player):
        game.resolved(self)

    def discard_handler(self, game, attacked_player, result):
        todis = min(2, len(attacked_player.hand))
        if len(result) != todis:
            game.whisper("You have to choose %s cards" % todis, attacked_player)
            return False
        game.discard_cards(result, attacked_player)
        return True

    def attack_handler(self, game, attacked_player, result):
        if result == 'Discard 2 cards':

            def f():
                ChangeSubPhaseEvent(self.id, 
                                     attacked_player,
                                     SP_PICKCARDSFROMHAND, 
                                     InfoToken("Discard two cards")).post(game.ev)
                (game.attack_cache)[attacked_player] = self.discard_handler

            return f
        else:
            pile = game.get_pile(Curse)
            game.take_card_from_pile(attacked_player, pile, safe=True,
                    to_hand=True)
        game.update_player()
        return True


class Tribute(Card):

    cardtype = ACTION
    cost = (5, 0)
    name = "Tribute"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):

        already_played = set()
        next_player = game.next_player()
        if next_player:
            for _ in xrange(2):
                c = game.reveal_top_card(next_player)
                if not c.name in already_played:
                    if c.cardtype & ACTION:
                        player.actions += 2
                    if c.cardtype & TREASURE:
                        player.money += 2
                    if c.cardtype & VICTORY:
                        game.draw_card(count=2)
                already_played.add(c.name)
                next_player.discardpile.add(c)
        game.resolved(self)


class Coppersmith(Card):

    cardtype = ACTION
    cost = (4, 0)
    name = "Coppersmith"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):

        def more_money_from_copper(_, player):
            player.money += 1

        game.add_action_step_handler(Copper, more_money_from_copper)
        game.add_buy_step_handler(Copper, more_money_from_copper)
        game.resolved(self)


class Scout(Card):

    cardtype = ACTION
    cost = (4, 0)
    name = "Scout"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.actions += 1
        cards = []
        for _ in xrange(4):
            card = game.reveal_top_card(player)
            if card:
                if card.cardtype & VICTORY:
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



class Conspirator(Card):
    
    known = True
    money = (2,0)
    
    cardtype = ACTION
    cost = (4, 0)
    name = "Conspirator"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.money += 2
        played_actions = [c for c in (game.last_played_cards)[player] if c.cardtype & ACTION]
        if len(played_actions) >= 2:
            game.draw_card()
            player.actions += 1

        game.resolved(self)


class Harem(Card):
    
    known = True
    money = (2,0)
    victoryPoints = 2

    cardtype = TREASURE | VICTORY
    cost = (6, 0)
    name = "Harem"

    def __init__(self):
        Card.__init__(self)

    def end_step(self, game, player):
        player.score += 2

    def buy_step(self, game, player):
        player.money += 2

    def action_step(self, game, player):
        self.buy_step(game, player)
        game.resolved(self)


class ShantyTown(Card):
    
    known = True
    extra_actions= 2

    cardtype = ACTION
    cost = (3, 0)
    name = "Shanty Town"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.actions += 2
        game.reveal_player_hand(player)
        if not player.hand.get_actions():
            game.yell("%s has no Action cards" % player.name)
            game.draw_card(count=2)

        game.resolved(self)


class MiningVillage(Card):

    cardtype = ACTION
    cost = (4, 0)
    name = "Mining Village"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.actions += 2
        game.draw_card()

        if self.virtual:
            game.resolved(self)
        else:
            game.ask_yes_no(self, 'Trash Mining Village for money?')

    def handler(self, game, player, result):
        if result == 'Yes':
            player.money += 2
            game.trash_card(player, self)
        game.update_player(player)
        game.resolved(self)
        return True


class Pawn(Card):

    cardtype = ACTION
    cost = (2, 0)
    name = "Pawn"

    def __init__(self):
        Card.__init__(self)
        self.actions_list = ("+1 card", "+1 action", "+1 buy", "+1")

    def action_step(self, game, player):
        game.ask(self, 'Choose one:', self.actions_list)

    def do_pawn(self, game, player, result):
        if result == "+1 card":
            game.draw_card()
        elif result == "+1 action":
            player.actions += 1
        elif result == "+1 buy":
            player.buys += 1
        elif result == "+1":
            player.money += 1

    def handler(self, game, player, result):
        self.do_pawn(game, player, result)

        remaining_actions = [i for i in self.actions_list if i != result]
        game.ask(self, 'Choose one:', remaining_actions, self.second_handler)

        return True

    def second_handler(self, game, player, result):
        self.do_pawn(game, player, result)
        game.resolved(self)
        return True


class Bridge(Card):
    
    known = True
    money = (1,0)
    extra_buys= 1

    cardtype = ACTION
    cost = (4, 0)
    name = "Bridge"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.buys += 1
        player.money += 1

        def mod(coins, potions):
            return (coins - 1, potions)

        game.add_cost_mod(mod)

        game.resolved(self)


class Steward(Card):

    cardtype = ACTION
    cost = (3, 0)
    name = "Steward"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.ask(self, 'Choose one:', ('+2 Cards', '+2', 'Trash 2 Cards'))

    def handler(self, game, player, result):

        if result == 'Trash 2 Cards':
            game.let_pick_from_hand(self, 'Trash 2 cards', self.trash_handler)
            return True

        if result == '+2 Cards':
            game.draw_card(count=2)
        elif result == '+2':
            player.money += 2

        game.resolved(self)
        return True

    def trash_handler(self, game, player, result):
        cards = [c for c in player.hand if c.id in result]
        if len(result) != 2 and not (len(result) < 2 and len(result) == 
                len(player.hand)):
            game.whisper("You have to trash two cards")
            return False

        [game.trash_card(player, c) for c in cards]
        game.resolved(self)
        return True


class GreatHall(Card):
    
    known = True
    victoryPoints = 1
    extra_actions= 1
    extra_cards= 1

    cardtype = ACTION | VICTORY
    cost = (3, 0)
    name = "Great Hall"

    def __init__(self):
        Card.__init__(self)

    def end_step(self, game, player):
        player.score += 1

    def action_step(self, game, player):
        player.actions += 1
        game.draw_card()
        game.resolved(self)


class Upgrade(Card):

    cardtype = ACTION
    cost = (5, 0)
    name = "Upgrade"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.actions += 1
        game.draw_card()
        game.let_pick_from_hand(self, "Pick a card to trash")

    def handler(self, game, player, result):
        if not player.hand:
            return True
        if len(result) != 1:
            game.whisper("You have to choose one card")
            return False

        card = player.hand.get_card(result[0])
        card_cost = game.get_cost(card)
        pile_with_exact_cost = [p for p in game.allpiles if game.get_cost(p)[0] == 
                                (card.cost)[0] + 1]
        game.trash_card(player, card)

        if not pile_with_exact_cost:
            game.whisper("There is no card that costs exactly %i" % (card_cost[0] + 
                         1))
            game.whisper("So no card taken")
            return True

        def pick_handler(game, player, result):
            pile = (p for p in game.allpiles if p.id == result).next()
            if game.get_cost(pile)[0] != card_cost[0] + 1:
                game.whisper("You have to pick a card with cost %i" % (card_cost[0] + 
                             1))
                return False
            game.take_card_from_pile(player, pile)
            game.resolved(self)
            return True

        game.let_pick_pile(self, "Pick a card costing %i" % (card_cost[0] + 1), pick_handler)
        return True


class Courtyard(Card):

    cardtype = ACTION
    cost = (2, 0)
    name = "Courtyard"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.draw_card(count=3)
        game.let_pick_from_hand(self, 'Choose a card to put on top of your Deck')

    def handler(self, game, player, result):
        if len(result) != 1:
            game.whisper("You have to choose one cards")
            return False

        card = player.hand.get_card(result[0])
        player.move_card_to_pile(card, player.drawpile)
        game.yell("%s puts a card on top of his deck" % player.name)
        game.resolved(self)
        return True


class Minion(Card):

    cardtype = ACTION | ATTACK
    cost = (5, 0)
    name = "Minion"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.actions += 1

        game.ask(self, 'Choose one:', ('+2',
                 'Discard hand cards and then +4 cards'))

    def handler(self, game, player, result):
        if result == '+2':
            player.money += 2
            game.resolved(self)
            return True
        elif result == 'Discard hand cards and then +4 cards':
            game.discard_hand(player)
            game.draw_card(count=4)
            def attack():
                game.attack(self, self.attack_handler, expect_answer=False)
            return attack

    def attack_handler(self, game, attacked_player, result):
        if len(attacked_player.hand) < 5:
            return True

        game.discard_hand(attacked_player)
        game.draw_card(attacked_player, 4)
        game.update_player(attacked_player)
        return True


class Ironworks(Card):

    cardtype = ACTION
    cost = (4, 0)
    name = "Ironworks"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.let_pick_pile(self, "Pick a card with cost up to 4")

    def handler(self, game, player, result):
        pile = game.get_pile(result)
        if not pile or game.get_cost(pile)[0] > 4 or (pile.cost)[1] > 0:
            game.whisper("You have to pick a card with cost <= 4")
            return False
        game.take_card_from_pile(player, pile)
        if pile.card.cardtype & ACTION:
            player.actions += 1
        if pile.card.cardtype & TREASURE:
            player.money += 1
        if pile.card.cardtype & VICTORY:
            game.draw_card()
        game.resolved(self)
        return True


class TradingPost(Card):

    cardtype = ACTION
    cost = (5, 0)
    name = "Trading Post"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        todis = min(len(player.hand), 2)
        if todis == 0:
            game.yell("%s has no card to trash" % player.name)
        else:
            game.let_pick_from_hand(self, 'Pick card(s) to trash')

    def handler(self, game, player, result):

        todis = min(len(player.hand), 2)
        if len(result) != todis:
            game.whisper("You have to choose %i cards" % todis)
            return False
        trash = [card for card in player.hand if card.id in result]
        [game.trash_card(player, card) for card in trash]
        if len(result) == 2:
            game.take_card_from_pile(player, game.get_pile(Silver), safe=
                    True, to_hand=True)
        return True


class Duke(Card):

    cardtype = VICTORY
    cost = (5, 0)
    name = "Duke"

    def __init__(self):
        Card.__init__(self)

    def end_step(self, game, player):
        duchy_cards = player.deck.get_all_of_card_class(Duchy)
        player.score += len(duchy_cards)


class Masquerade(Card):

    cardtype = ACTION
    cost = (3, 0)
    name = "Masquerade"

    def __init__(self):
        Card.__init__(self)
        self.pending = 0
        self.choosed = {}

    def action_step(self, game, player):
        self.pending = 0
        self.choosed = {}

        game.draw_card(count=2)

        p = game.let_all_players_pick(self, 'Choose a card to pass to the left')

        self.pending = len(p)

    def handler(self, game, player, result):
        if len(player.hand) > 0 and len(result) != 1:
            game.whisper("You have to choose one card")
            return False

        if len(player.hand) > 0:
            (self.choosed)[player.id] = result[0] if result else None

        self.pending -= 1

        if player is game.active_player:
            if self.pending:
                return LateCall(lambda p=player, g=game: self.masq_handler(g,
                                p))
            else:
                self.masq_handler(game, player)

        return True

    def masq_handler(self, game, player):
        if len(self.choosed) > 1:
            for pid in self.choosed:
                player = game.get_player_by_id(pid)
                next_player = game.next_player(player)
                card = player.hand.get_card((self.choosed)[pid])
                player.hand.remove(card)
                player.deck.remove(card)
                next_player.hand.add(card)
                next_player.deck.add(card)

        game.update_player()

        game.enter_subphase(SubPhaseInfo(SP_PICKCARDSFROMHAND, card=self,
                            callback=self.trash_handler, info=
                            "Pick up to one card to trash"))

    def trash_handler(self, game, player, result):
        if len(result) > 1:
            game.whisper("You have to choose one or zero cards")
            return False

        trash = [card for card in player.hand if card.id in result]
        [game.trash_card(player, card) for card in trash]
        game.resolved(self)
        return True


