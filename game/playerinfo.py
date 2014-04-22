#!/usr/bin/python
# -*- coding: utf-8 -*-


class PlayerInfo(object):

    def __init__(
        self,
        player_name,
        hand_size,
        drawpile_size,
        discardpile_size,
        actions,
        buys,
        money,
        current,
        score,
        potion,
        id,
        ):

        self.player_name = player_name
        self.hand_size = hand_size
        self.drawpile_size = drawpile_size
        self.discardpile_size = discardpile_size
        self.actions = actions
        self.buys = buys
        self.money = money
        self.current = current
        self.score = score
        self.potion = potion
        self.id = id

    def __str__(self):
        return """player_name: %s
hand_size: %i
drawpile_size: %i
discardpile_size: %i
actions: %i 
buys: %i 
money: %i 
current: %i 
score: %i
potion: %i""" % \
            (
            self.player_name,
            self.hand_size,
            self.drawpile_size,
            self.discardpile_size,
            self.actions,
            self.buys,
            self.money,
            self.current,
            self.score,
            self.potion,
            )


