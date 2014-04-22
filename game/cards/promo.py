#!/usr/bin/python
# -*- coding: utf-8 -*-

from game.cards.card import Card, ACTION


class WalledVillage(Card):

    cardtype = ACTION
    cost = (4, 0)
    name = "Walled Village"

    def __init__(self):
        Card.__init__(self)

    def action_step(self, game, player):
        game.draw_card()
        player.actions += 2

    def cleanup_step(self, game, player):
        number_of_action_cards = len([c for c in player.board if c.cardtype &
                ACTION])
        if number_of_action_cards <= 2:
            game.ask_yes_no(self,
                            'Put Walled Village on top of your deck?')

    def handler(self, game, player, result):
        if result == 'Yes':
            player.board.remove(self)
            player.drawpile.add(self)
            game.yell("%s puts Walled Village on top of his deck" %
                      player.name)
        game.resolved(self)
        return True


