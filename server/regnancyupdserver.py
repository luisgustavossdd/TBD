#!/usr/bin/python
# -*- coding: utf-8 -*-

from SocketServer import BaseRequestHandler, UDPServer
from framework.async import PP_QUIT, get_timeout_pipe
import logging
from framework.event import CPUSpinnerController, EventManager, QuitEvent


class Handler(BaseRequestHandler):

    def handle(self):
        socket = (self.request)[1]
        socket.sendto((RegnancyUDPServer.regnancy_server_address)[0] +
                      ':' + str((RegnancyUDPServer.regnancy_server_address)[1]),
                      self.client_address)


class RegnancyUDPServer(UDPServer):

    def __init__(self, regnancy_server_address):

        for port in xrange(12000, 25000):
            try:
                logging.info("UDPServer starts")
                UDPServer.__init__(self, ("", port), Handler)
                logging.info("UDPServer runs %i", port)
                break
            except:
                pass

        self.timeout = 0.05
        RegnancyUDPServer.regnancy_server_address = \
            regnancy_server_address
        self.running = True

    def notify(self, event):
        pass

    def handle_tickevent(self, event):
        self.handle_request()
        
        if not self.pipe.check():
            self.running = False
            QuitEvent().post(self.ev)
        
    def handle_quitevent(self, event):
        logging.info("Shutting down UDP Server")
        self.pipe.send([PP_QUIT])

    def Launch(self, pipe):
        logging.info("UDP Launched")
        self.pipe = get_timeout_pipe(pipe)
        spinner = CPUSpinnerController()
        self.ev = EventManager()
        self.ev.register_listener(self)
        self.ev.register_listener(spinner)
        spinner.run(self.ev)

        


