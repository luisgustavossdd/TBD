#!/usr/bin/python
# -*- coding: utf-8 -*-

import framework.networking as nwp

from framework.PodSixNet.Connection import ConnectionListener
from framework.locals import *
from framework.event import *
from game.pile import KingdomPile
import socket

class RegnancyClient(ConnectionListener):

    def __init__(self):
        self.messages = []
        self.sub_id = None
        self.global_gamestate = None
        self.result = None
        self.net_handler = {PLAYERINFO: self.proceed_playerinfo,
                            PHASE: self.proceed_phase,
                            SUBID: self.proceed_subid,
                            HAND: self.proceed_hand,
                            BOARD: self.proceed_board,
                            BOARDSETUP: self.proceed_boardsetup,
                            BOARDCOMMON: self.proceed_boardcommon}
    def run(self, client):
        ev = EventManager()
        client.ev = ev
        self.ev = ev
        spinner = CPUSpinnerController()

        ev.register_listener(self)
        ev.register_listener(spinner)
        ev.register_listener(client)

        spinner.run(ev)

    def handle_requestconnectevent(self, event):
        (host, port) = event.con_data
        self.con_data = (host, port)
        self.Connect((host, port))

    def handle_tickevent(self, event):
        if hasattr(self, 'connection'):
            self.connection.Pump()
            self.Pump()

    def handle_playcardevent(self, event):
        self.connection.Send({ACTION: RESPONSE, 
                              PLAYCARD: nwp.pack(event.card_id), 
                              ID: self.id})
    
    def handle_answerevent(self, event):
        self.connection.Send({ACTION: RESPONSE, 
                              ANSWER: nwp.pack(event.answer),
                              ID: self.id, SUBID: nwp.pack(self.sub_id)})

    def handle_buycardevent(self, event):
        self.connection.Send({ACTION: RESPONSE, 
                              BUYFROMPILE: nwp.pack(event.pile_id),
                              ID: self.id})

    def handle_requeststartgame(self, event):
            self.connection.Send({ACTION: REQUEST, 
                                  VALUE: GAMESTART, ID: self.id,
                                  INFO: event.deck_name})
            
    def handle_requestchangename(self, event):
        self.connection.Send({ACTION: CHANGENAME, 
                              VALUE: event.name,
                              ID: self.id})
        
    def handle_endphaseevent(self, event):
        self.connection.Send({ACTION: REQUEST, 
                              VALUE: ENDPHASE, 
                              INFO: event.phase,
                              ID: self.id})

    def notify(self, event):
        pass

    def add_message(self, message):

        self.messages.append(message)
        MessageEvent(message).post(self.ev)

    def Network_connected(self, data):
        logging.debug("connected")

    def Network_error(self, data):
        ConnectionFailed(*self.con_data).post(self.ev)
        logging.error(data)

    def Network_initial(self, data):
        self.id = data[ID]
        (h, p) = self.con_data
        ConnectionSuccess(h, p, self.id).post(self.ev)

    def Network_setmaster(self, data):
        SetMasterEvent(data[VALUE]).post(self.ev)

    def Network_message(self, data):
        self.add_message(data[MESSAGE])

    def Network_end(self, data):
        result = nwp.unpack(data[RESULT])
        EndGameEvent(result).post(self.ev)

    def Network_start(self, data):
        GameStartedEvent().post(self.ev)

    def proceed_playerinfo(self, data):
        PlayerInfoEvent(nwp.unpack(data[PLAYERINFO])).post(self.ev)
    
    def proceed_phase(self, data):
        phase = data[PHASE]
        client = data[CLIENTID]

        GlobalPhaseChangedEvent(phase).post(self.ev)
        if client == self.id:
            PhaseChangedEvent(phase).post(self.ev)
            
    def proceed_subid(self, data):
        if data[CLIENTID] == self.id:
            info = nwp.unpack(data[INFO]) if INFO in data else None
            self.sub_id = nwp.unpack(data[SUBID])
            SubPhaseChangedEvent(data[SUBPHASE], info, self.sub_id).post(self.ev)
        
    def proceed_hand(self, data):
        NewHandEvent(nwp.unpack(data[HAND]), nwp.unpack(data[DECK])).post(self.ev)
        
    def proceed_board(self, data):
        NewBoardEvent(nwp.unpack(data[BOARD])).post(self.ev)
        
    def proceed_boardsetup(self, data):
        newboardsetup = nwp.unpack(data[BOARDSETUP])
        self.boardsetup = []
        for item in newboardsetup:
            pile = KingdomPile(item[1], item[2])
            pile.id = item[0]
            pile.calc_cost = item[3]
            self.boardsetup.append(pile)
        NewBoardSetupEvent(self.boardsetup).post(self.ev)
    
    def proceed_boardcommon(self, data):
        newboardcommon = nwp.unpack(data[BOARDCOMMON])
        self.boardcommon = []
        for item in newboardcommon:
            pile = KingdomPile(item[1], item[2])
            pile.id = item[0]
            pile.calc_cost = item[3]
            self.boardcommon.append(pile)
        NewBoardCommonEvent(self.boardcommon).post(self.ev)
    
    def Network_update(self, data):
        for key in self.net_handler:
            if key in data:
                self.net_handler[key](data)
                return

            
        

