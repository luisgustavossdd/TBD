#!/usr/bin/python
# -*- coding: utf-8 -*-

from client.regnancyclient import RegnancyClient
from framework.async import ProcessProxy
from aiclient import get_aiclient

class BotThread(object):

    """Simple Thread that launches a Bot"""

    def __init__(self, port):
        self.port = port
        self.pp = None

    def start(self):

        def f(pipe):
            client = get_aiclient(pipe)
            RegnancyClient().run(client)

        self.pp = ProcessProxy(f)
        self.pp.start()

    def join(self):
        self.pp.join()

    def keep_alive(self):
        self.pp.keep_alive()


