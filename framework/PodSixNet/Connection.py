#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
A client\'s connection to the server.

This module contains two components: a singleton called \'connection\' and a class called \'ConnectionListener\'.

\'connection\' is a singleton instantiation of an EndPoint which will be connected to the server at the other end. It\'s a singleton because each client should only need one of these in most multiplayer scenarios. (If a client needs more than one connection to the server, a more complex architecture can be built out of instantiated EndPoint()s.) The connection is based on Python\'s asyncore and so it should have it\'s polling loop run periodically, probably once per gameloop. This just means putting "from Connection import connection; connection.Pump()" somewhere in your top level gameloop.

Subclass ConnectionListener in order to have an object that will receive network events. For example, you might have a GUI element which is a label saying how many players there are online. You would declare it like \'class NumPlayersLabel(ConnectionListener, ...):\' Later you\'d instantitate it \'n = NumPlayersLabel()\' and then somewhere in your loop you\'d have \'n.Pump()\' which asks the connection singleton if there are any new messages from the network, and calls the \'Network_\' callbacks for each bit of new data from the server. So you\'d implement a method like "def Network_players(self, data):" which would be called whenever a message from the server arrived which looked like {"action": "players", "number": 5}.
'''

from EndPoint import EndPoint


class ConnectionListener:

    '''
\tLooks at incoming data and calls "Network_" methods in self, based on what messages come in.
\tSubclass this to have your own classes monitor incoming network messages.
\tFor example, a method called "Network_players(self, data)" will be called when a message arrives like:
\t\t{"action": "players", "number": 5, ....}
\t'''

    def Connect(self, *args, **kwargs):
        self.connection = EndPoint()
        self.connection.DoConnect(*args, **kwargs)

        self.Pump()

    def Pump(self):
        for data in self.connection.GetQueue():
            [getattr(self, n)(data) for n in ("Network_" + data['action'], "Network") if hasattr(self, n)]


