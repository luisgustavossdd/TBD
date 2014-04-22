#!/usr/bin/python
# -*- coding: utf-8 -*-

from game.player import Player
from framework.PodSixNet.Channel import Channel
from framework.regnancyexception import NotEnoughMoneyException, \
    PileIsEmptyException
from framework.locals import *
import framework.networking as nwp
import logging
import game


class RegnancyChannel(Channel):

    """This is the server representation of a single connected client."""

    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)
        self.id = str(self._server.NextId())
        intid = int(self.id)
        self.player = Player(self.id, self._server.game, intid)

    def Close(self):
        """When being closed, inform the server"""

        self._server.delete_player(self)

    def get_sender(self, data):
        """Returns the client which has send this data package or None"""
        return next(p for p in self._server.clients if p.id == data[ID])
        
    def Network_changename(self, data):
        """Called when a player wants to changes its name"""

        client = self.get_sender(data)
        client.player.name = data[VALUE]
        self._server.send_playerlist()
        #logging.debug("player %s changed name to %s", data[ID], data[VALUE])
        
    def Network_request(self, data):
        client = self.get_sender(data)
        if data[VALUE] == GAMESTART:
            if self._server.game.running:
                client.Send({ACTION: MESSAGE, MESSAGE: "Game already running"})
                return
            if len(self._server.clients) >= 2 or 1: # or game.global_options.debug_mode:
                self._server.start_game(data)
            else:
                client.Send({ACTION: MESSAGE, MESSAGE: "Waiting for a second player"})
        elif data[VALUE] == ENDPHASE:
            logging.debug("%s wants to end phase", client.player.name)
            if client.player == self._server.game.active_player and (not data[INFO] or data[INFO] == self._server.game.phase):
                self._server.game.endphase(client.player)

    def Network_response(self, data):
        client = self.get_sender(data)

        if BUYFROMPILE in data:
            try:
                self._server.game.buy_card(client.player, nwp.unpack(data[BUYFROMPILE]))
            except (NotEnoughMoneyException, PileIsEmptyException):
                pass

        if PLAYCARD in data:
            self._server.game.play_card(client.player, nwp.unpack(data[PLAYCARD]))

        if ANSWER in data:
            self._server.game.answered(client.player, nwp.unpack(data[ANSWER]), nwp.unpack(data[SUBID]))
        

