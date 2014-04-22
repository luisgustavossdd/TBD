#!/usr/bin/python
# -*- coding: utf-8 -*-

from framework.PodSixNet.Server import Server
from framework.locals import *
from game import game, global_options
from regnancychannel import RegnancyChannel
from time import sleep
from weakref import WeakKeyDictionary
import framework.networking as nwp
from framework.async import PP_QUIT, TimeOutToken, DummyTimeOutPipe, TimeOutPipe,\
    get_timeout_pipe
from game.infotoken import InfoToken
from framework.misc import get_id
from threading import Lock
import logging
from framework.event import EventManager, CPUSpinnerController, QuitEvent

class RegnancyServer(Server):

    def __init__(self, *args, **kwargs):
        self.running = True
        self.clients = WeakKeyDictionary()
        self.masterplayer = None

        self.localaddr = (nwp.get_lan_ip(), global_options.port)
        Server.__init__(self, RegnancyChannel, localaddr=self.localaddr)
        self.addr = self.socket.getsockname()
        self.ev = EventManager()
        self.ev.register_listener(self)
        self.__game = game.Game(self.ev)
        self.ev.register_listener(self.__game)
        self.__lock = Lock()
        
    @property
    def game(self):
        with self.__lock:
            return self.__game

    def NextId(self):
        return get_id()
        
    def Connected(self, channel, addr):
        self.add_player(channel)

    def add_player(self, client):
        (self.clients)[client] = True
        client.Send({ACTION: INITIAL, MESSAGE: "Welcome to Regnancy-Server at %s:%i" %
                    ((self.localaddr)[0], (self.localaddr)[1]), ID: client.id})

        if len(self.clients) == 1:
            self.masterplayer = client
            client.Send({ACTION: SETMASTER, VALUE: True})
        self.send_playerlist()

    def delete_player(self, client):
        logging.warning("Deleting Player %s", str(client.addr))
        self.send_to_all({ACTION: MESSAGE, MESSAGE: "player %s (%s) left the server" %
                         (client.id, client.player.name)})
        try:
            del (self.clients)[client]
        except:
            pass
        self.send_playerlist()
        if self.game.running:
            raise Exception("Player died while playing")

    def get_client(self, player):
        assert player, "player is None"
        return next(c for c in self.clients if c.player.id == player.id)

    def get_playerinfos(self):
        infos = []
        for c in self.clients:
            info = c.player.create_info()
            info.player_id = c.id
            infos.append(info)
        return infos

    def send_playerlist(self):
        infos = self.get_playerinfos()
        if self.game.running:
            if not len([p for p in infos if p.current]) == 1:  # or len(infos) < 2:
                for i in infos:
                    print i
                    raise Exception("no active player???")

        self.send_to_all({ACTION: UPDATE, PLAYERINFO: nwp.pack(infos)})

    def send_to_all(self, data):
        assert data, "data is None"

        [p.Send(data) for p in self.clients]
        self.Pump()  #ensure data is send

    def handle_changephaseevent(self, event):
        assert event.player, "player is None"
        assert event.phase, "phase is None"
        self.send_to_all({ACTION: UPDATE, 
                          PHASE: event.phase, 
                          CLIENTID: self.get_client(event.player).id})

    def handle_changesubphaseevent(self, event):
        assert event.player, "player is None"
        assert event.subphase, "subphase is None"

        if event.info:
            assert isinstance(event.info, InfoToken)
        
        self.send_to_all({ACTION: UPDATE, 
                          SUBID: nwp.pack(event.card_id),
                          SUBPHASE: event.subphase, 
                          INFO: nwp.pack(event.info),
                          CLIENTID: self.get_client(event.player).id})

    def handle_changehandevent(self, event):
        assert event.player, "player is None"
        self.__send_hand(event.player)

    def __send_hand(self, player):
        for c in player.hand: #TODO: Should be done in game
            c.calc_cost = self.game.get_cost(c)
            
        self.get_client(player).Send({ACTION: UPDATE, 
                                      HAND: nwp.pack(player.hand),
                                      DECK: nwp.pack(player.deck)})

    def handle_changeboardevent(self, event):
        assert event.player, "player is None"
        for c in event.player.board: #TODO: Should be done in game
            c.calc_cost = self.game.get_cost(c)

        self.send_to_all({ACTION: UPDATE, 
                          BOARD: nwp.pack(event.player.board)})

    def handle_messageevent(self, event):
        assert event.message, "message is None"
        #logging.debug(event.message)
        m = {ACTION: MESSAGE, MESSAGE: event.message}
        if event.reciever:
            self.get_client(event.reciever).Send(m)
        else:
            self.send_to_all(m)

    def handle_playerinfoevent(self, event):
        self.send_to_all({ACTION: UPDATE, PLAYERINFO: nwp.pack(event.playerinfos)})

    def handle_gameendevent(self, event):
        self.send_to_all({ACTION: END, RESULT: nwp.pack(event.result)})
        self.running = False
        
    def handle_changepilesevent(self, event):
        self.__send_piles()

    def __send_piles(self):
        self.send_to_all({ACTION: UPDATE, BOARDSETUP: nwp.pack([(pile.id,
                         pile.card, len(pile), self.game.get_cost(pile))
                         for pile in self.game.kingdompiles])})

        self.send_to_all({ACTION: UPDATE, BOARDCOMMON: nwp.pack([(pile.id,
                         pile.card, len(pile), self.game.get_cost(pile))
                         for pile in self.game.commonpiles])})

    def start_game(self, data):
        self.game_running = True

        deck_name = data[INFO]
        self.game.setup(deck_name, [c.player for c in self.clients])

        self.send_playerlist()
        self.__send_piles()

        for client in self.clients:
            self.__send_hand(client.player)

        self.send_to_all({ACTION: START, MESSAGE: "game started"})

    def handle_quitevent(self, event):
        sleep(0.0001)
        self.close()
        self.pipe.send([PP_QUIT])

    def handle_tickevent(self, event):
        if not self.pipe.check():
            self.running = False
            QuitEvent().post(self.ev)
            
        if self.game.running:
            self.game.update()
        self.Pump()
        sleep(0.01)
    
    def notify(self, event):
        pass
        
    def Launch(self, pipe=None):
        self.pipe = get_timeout_pipe(pipe)
        spinner = CPUSpinnerController()
        self.ev.register_listener(spinner)
        spinner.run(self.ev)

