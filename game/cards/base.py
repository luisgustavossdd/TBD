#!/usr/bin/python
# -*- coding: utf-8 -*-

from game.cards.card import Card, ACTION, ATTACK, VICTORY, REACTION, TREASURE, \
    DURATION
from game.cards.common import Silver, Copper, Curse
from game.gametrigger import T_ATTACK


class Bureaucrat(Card):

    cardtype = ACTION | ATTACK
    cost = (4, 0)
    name = "Bureaucrat"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.take_card_from_pile(player, game.get_pile(Silver), safe=
                                 True, to_deck=True)
        
        game.attack_let_pick_from_hand(self, "Put a Victory Card on top of your deck")

    def attack_handler(self, game, attacked_player, result):
        if not attacked_player.hand.get_victories():
            game.reveal_player_hand(attacked_player)
            return True

        if len(result) != 1:
            game.whisper("You have to choose one Victory card", attacked_player)
            return False

        card = attacked_player.hand.get_card(result[0])
        if not card.cardtype & VICTORY:
            game.whisper("You have to choose a Victory card", attacked_player)
            return False

        attacked_player.hand.remove(card)
        attacked_player.drawpile.add(card)
        game.update_player(attacked_player)
        game.yell("%s puts %s on top" % (attacked_player.name, card.name))
        return True


class Moneylender(Card):

    cardtype = ACTION
    cost = (4, 0)
    name = "Moneylender"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        try:
            cop = (card for card in player.hand if isinstance(card,
                    Copper)).next()
            game.trash_card(player, cop)
            player.money += 3
        except StopIteration:
            pass
        game.resolved(self)


class Woodcutter(Card):

    cardtype = ACTION
    cost = (3, 0)
    name = "Woodcutter"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.buys += 1
        player.money += 2
        game.resolved(self)


class ThroneRoom(Card):

    cardtype = ACTION
    cost = (4, 0)
    name = "Throne Room"

    def __init__(self):
        Card.__init__(self)

    def begin_step(self, game, player):
        """ 
    Called when Throne Room was used to play a Duration Card, so Throne Room
    is still in play at the beginning of the turn.
    """

        player.hand.add(self.doubled_card)
        game.play_card(player, self.doubled_card.id, free=True,
                       is_duration=True)
        game.trash_card(player, self.doubled_card, silent=True)
        self.doubled_card = None

    def action_step(self, game, player):
        if not [c for c in player.hand if c.cardtype & ACTION]:
            return

        game.let_pick_from_hand(self, 'Pick a card to play twice')
        

    def handler(self, game, player, result):

        if len(result) != 1:
            game.whisper("You have to choose one card")
            return False

        card = (c for c in player.hand if c.id in result).next()
        if not card.cardtype & ACTION:
            game.whisper("You have to choose a Action card")
            return False

        doubled_card = card.copy()

        if card.cardtype & DURATION:
            player.durations.add(self)

        def on_resolved(game, player):
            """Called when the first card is resolved, so we can now play the second one"""

            self.doubled_card = doubled_card.copy()  #copy the already played doubled_card, so instance members get copied
            game.trash_card(player, doubled_card)
            player.hand.add(card)

            def r(*args):
                game.resolved(self)

            game.on_resolve(card, r)
            game.play_card(player, card.id, free=True)

        game.on_resolve(doubled_card, on_resolved)
        player.hand.add(doubled_card)
        player.hand.remove(card)
        game.play_card(player, doubled_card.id, free=True)
        return True


class CouncilRoom(Card):

    cardtype = ACTION
    cost = (5, 0)
    name = "Council Room"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.draw_card(count=4)
        player.buys += 1

        [game.draw_card(p) for p in game.players if p is not player]
        game.resolved(self)


class Library(Card):

    cardtype = ACTION
    cost = (5, 0)
    name = "Library"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        self.picked_cards = []
        self.last_card = None
        self.handler(game, player)

    def handler(self, game, player):

        def do_library(*args, **kwargs):

            def handle_answer(_, ap, result):
                if result == 'Yes':
                    self.picked_cards.append(self.last_card)
                else:
                    player.discardpile.add(self.last_card)
                return True

            def take_picked_card():
                for card in self.picked_cards:
                    player.hand.add(card)

            if len(self.picked_cards) + len(player.hand) < 7:
                card = game.reveal_top_card(player)
                if card:
                    if card.cardtype & ACTION:
                        self.last_card = card
                        game.ask_yes_no(self, 'Take %s?' % card.name,
                                handle_answer, do_library)
                    else:
                        player.hand.add(card)
                        do_library()
                else:
                    take_picked_card()
                    game.update_player(player)
                    return True
            else:
                take_picked_card()
                game.update_player(player)
                return True

        do_library()


class Village(Card):

    cardtype = ACTION
    cost = (3, 0)
    name = "Village"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.draw_card()
        player.actions += 2
        game.resolved(self)


class Market(Card):

    cardtype = ACTION
    cost = (5, 0)
    name = "Market"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.money += 1
        player.buys += 1
        player.actions += 1
        game.draw_card()
        game.resolved(self)


class Chapel(Card):

    cardtype = ACTION
    cost = (2, 0)
    name = "Chapel"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.let_pick_from_hand(self, "Trash up to 4 cards" )
        
    def handler(self, game, player, result):
        if len(result) > 4:
            game.whisper("You have to trash up to 4 cards")
            return False
        trash = [card for card in player.hand if card.id in result]
        [game.trash_card(player, card) for card in trash]
        game.resolved(self)
        return True


class Workshop(Card):

    cardtype = ACTION
    cost = (3, 0)
    name = "Workshop"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.let_pick_pile(self, "Pick a card with cost up to 4")
        
    def handler(self, game, player, result):
        pile = game.get_pile(result)
        if not pile or game.get_cost(pile)[0] > 4 or (pile.cost)[1] > 0:
            game.whisper("You have to pick a card with cost up to 4")
            return False
        game.take_card_from_pile(player, pile)
        game.resolved(self)
        return True


class Mine(Card):

    cardtype = ACTION
    cost = (5, 0)
    name = "Mine"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        if not player.hand.get_treasures():
            game.whisper("You have no treasure in your hand")
            return
        game.let_pick_from_hand(self, "Pick a treasure card to trash")

    def handler(self, game, player, result):
        if len(result) != 1:
            game.whisper("You have to choose one card")
            return False

        card = (c for c in player.hand if c.id in result).next()
        if not card.cardtype & TREASURE:
            game.whisper("You have to choose a treasure card")
            return False

        game.trash_card(player, card)

        max_cost = game.get_cost(card)[0] + 3

        def pick_handler(game, player, result):
            pile = game.get_pile(result)
            if not pile or game.get_cost(pile)[0] > max_cost or (pile.cost)[1] > 0:
                game.whisper("You have to pick a card with cost up to %i" %
                             max_cost)
                return False
            if not pile.card.cardtype & TREASURE:
                game.whisper("You have to pick a treasure card")
                return False
            game.take_card_from_pile(player, pile, to_hand=True)
            game.resolved(self)
            return True

        game.let_pick_pile(self, "Pick a treasure card with cost max %i" % max_cost, pick_handler)

        return True


class Moat(Card):

    cardtype = ACTION | REACTION
    cost = (2, 0)
    name = "Moat"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.draw_card(count=2)
        game.resolved(self)

    def handle_trigger(self, trigger):
        if trigger == T_ATTACK:
            return True

class Witch(Card):

    cardtype = ACTION | ATTACK
    cost = (5, 0)
    name = "Witch"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.draw_card(count=2)

        game.attack(self, self.attack_handler, expect_answer=False)

    def attack_handler(self, game, attacked_player, result):
        curse_pile = game.get_pile(Curse)
        game.take_card_from_pile(attacked_player, curse_pile, safe=True)
        return True


class Adventurer(Card):

    cardtype = ACTION
    cost = (6, 0)
    name = "Adventurer"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        num_treasures = len(player.discardpile.get_treasures()) + len(player.drawpile.get_treasures())

        def draw():
            c = game.reveal_top_card(player)
            if c.cardtype & TREASURE:
                player.hand.add(c)
                return True
            else:
                player.discardpile.add(c)
                return False

        if num_treasures < 2:
            for _ in player.drawpile:
                draw()
            for _ in xrange(len(player.discardpile)):
                draw()
        else:
            t = 0
            while t < 2:
                if draw():
                    t += 1

        game.resolved(self)


class Spy(Card):

    cardtype = ACTION | ATTACK
    cost = (4, 0)
    name = "Spy"

    def __init__(self):
        Card.__init__(self)
        self.revealed = {}

    def action_step(self, game, player):
        self.revealed = {}
        game.draw_card()
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

        def do_spy(*args, **kwargs):
            try:
                (p, card) = gen.pop()

                def handle_answer(_, ap, result):
                    if result == 'Yes':
                        ap.discardpile.add(card)
                    else:
                        ap.drawpile.add(card)
                    return True

                game.ask_yes_no(self, "Discard %s's %s?" % (p.name, card.name),
                                handle_answer, do_spy, card)
            except IndexError:

                return True

        do_spy()


class Thief(Card):

    cardtype = ACTION | ATTACK
    cost = (4, 0)
    name = "Thief"

    def __init__(self):
        Card.__init__(self)
        self.revealed = {}

    def action_step(self, game, player):
        self.revealed = {}
        game.attack(self, self.attack_handler, expect_answer=False,
                    on_restore_callback=self.handler)

    def attack_handler(self, game, attacked_player, result):
        (self.revealed)[attacked_player.id] = (game.reveal_top_card(attacked_player),
                game.reveal_top_card(attacked_player))
        return True

    def handler(self, game, player):
        gen = [(game.get_player_by_id(pid), (self.revealed)[pid]) for pid in
               self.revealed]

        def do_thief(*args, **kwargs):
            try:
                (p, (card1, card2)) = gen.pop()

                def handle_answer(_, ap, result):
                    if result == "Do nothing":
                        return True

                    (action, cardname) = result.split(' ')

                    card = (c for c in (card1, card2) if c.name ==
                        cardname).next()

                    if card1 and not card1 is card:
                        p.discardpile.add(card1)
                    if card2 and not card2 is card:
                        p.discardpile.add(card2)

                    if action == 'Trash':
                        game.trash_card(p, card)
                    else:
                        game.active_player.discardpile.add(card)
                    return True

                answers = []
                for card in (card1, card2):
                    if card and card.cardtype & TREASURE:
                        answers.append("Trash " + card.name)
                        answers.append("Steal " + card.name)
                if not answers:
                    answers.append("Do nothing")

                game.ask(self, 'Attack against %s' % p.name, answers,
                         handle_answer, do_thief)
            except IndexError:
                return True

        do_thief()


class Festival(Card):

    cardtype = ACTION
    cost = (5, 0)
    name = "Festival"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.money += 2
        player.buys += 1
        player.actions += 2
        game.resolved(self)


class Cellar(Card):

    cardtype = ACTION
    cost = (2, 0)
    name = "Cellar"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.actions += 1
        game.let_pick_from_hand(self, "Discard any number of cards")

    def handler(self, game, player, result):
        cards = [c for c in player.hand if c.id in result]
        [game.discard_card(player, c) for c in cards]
        game.draw_card(count=len(cards))
        game.resolved(self)
        return True


class Militia(Card):

    cardtype = ACTION | ATTACK
    cost = (4, 0)
    name = "Militia"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.money += 2
        game.attack_let_pick_from_hand(self, "Discard down to three cards")

    def attack_handler(self, game, attacked_player, result):
        todis = max(0, len(attacked_player.hand) - 3)
        if len(result) != todis:
            game.whisper("You have to choose %s cards" % todis, attacked_player)
            return False
        discard = [card for card in attacked_player.hand if card.id in
                   result]
        [game.discard_card(attacked_player, card) for card in discard]
        return True


class Gardens(Card):

    cardtype = VICTORY
    cost = (4, 0)
    name = "Gardens"

    def __init__(self):
        Card.__init__(self)

    def end_step(self, game, player):
        player.score += len(player.deck) / 10


class Feast(Card):

    cardtype = ACTION
    cost = (4, 0)
    name = "Feast"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.let_pick_pile(self, "Pick a card with cost up to 5")

    def handler(self, game, player, result):
        pile = (p for p in game.allpiles if p.id == result).next()
        if game.get_cost(pile)[0] > 5 or (pile.cost)[1] > 0:
            game.whisper("You have to pick a card with cost up to 5")
            return False
        game.take_card_from_pile(player, pile)
        game.trash_card(player, self)
        game.resolved(self)
        return True


class Chancellor(Card):

    cardtype = ACTION
    cost = (3, 0)
    name = "Chancellor"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.money += 2
        game.ask_yes_no(self, 'Put your deck into your discard pile?')

    def handler(self, game, player, result):
        if result == 'Yes':
            [player.discardpile.add(player.drawpile.take()) for _ in
             xrange(len(player.drawpile))]
            game.yell('%s puts his deck into his discard pile' % player.name)
            game.update_player(player)
        game.resolved(self)
        return True


class Laboratory(Card):

    cardtype = ACTION
    cost = (5, 0)
    name = "Laboratory"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        player.actions += 1
        game.draw_card(count=2)
        game.resolved(self)


class Remodel(Card):

    cardtype = ACTION
    cost = (4, 0)
    name = "Remodel"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.let_pick_from_hand(self, "Pick a card to remodel")

    def handler(self, game, player, result):
        if not player.hand:
            return True
        if len(result) != 1:
            game.whisper("You have to choose one card")
            return False

        card = (card for card in player.hand if card.id in result).next()
        card_cost = game.get_cost(card)

        def pick_handler(game, player, result):
            pile = game.get_pile(result)
            if not pile or game.get_cost(pile)[0] > card_cost[0] + 2 or (pile.cost)[1] > \
                card_cost[1]:
                game.whisper("You have to pick a card with cost up to %i/%i" %
                             (card_cost[0] + 2, card_cost[1]))
                return False
            game.take_card_from_pile(player, pile)
            game.resolved(self)
            return True

        game.trash_card(player, card)

        game.let_pick_pile(self, 
                           "Pick a card costing up to %i/%i" % (card_cost[0] +
                            2, card_cost[1]), pick_handler)
        return True


class Smithy(Card):

    cardtype = ACTION
    cost = (4, 0)
    name = "Smithy"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.draw_card(count=3)
        game.resolved(self)


