#!/usr/bin/python
# -*- coding: utf-8 -*-

from framework.async import ProcessProxy
from server.regnancyserver import RegnancyServer
from server.regnancyupdserver import RegnancyUDPServer


class SThread(object):

    def __init__(self, f):
        assert f
        self.f = f
        self.pp = None

    def start(self):
        self.pp = ProcessProxy(self.f)
        self.pp.start()

    def join(self):
        self.pp.join()

    def keep_alive(self):
        self.pp.keep_alive()

    def poll(self):
        return self.pp.poll()


class ServerThread(SThread):

    """Simple Thread that launches a RegnancyServer"""

    addr = None

    def __init__(self):

        def f(pipe):
            rs = RegnancyServer()
            pipe.send(rs.addr)
            rs.Launch(pipe)

        SThread.__init__(self, f)


class UDPServerThread(SThread):

    def __init__(self, addr):

        def f(pipe):
            RegnancyUDPServer(addr).Launch(pipe)

        SThread.__init__(self, f)


