#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import traceback
from errno import EWOULDBLOCK
from async import asynchat
from rencode import loads, dumps

from threading import Lock
class IdGenProxy(object):

    def __init__(self):
        self.__lock = Lock()
    
        def idgen():
            i = 0
            while 1:
                i += 1
                yield i
                
        self.__id_generator = idgen()
    
    def next(self):
        with self.__lock:
            return self.__id_generator.next()
        
id = IdGenProxy()


class Channel(asynchat.async_chat):

    endchars = '\0---\0'

    def __init__(self, conn=None, addr=(), server=None, map=None):
        asynchat.async_chat.__init__(self, conn, map)
        self.addr = addr
        self._server = server
        self._ibuffer = ""
        self.set_terminator(self.endchars)
        self.sendqueue = []

    def collect_incoming_data(self, data):
        self._ibuffer += data

    def found_terminator(self):
        data = loads(self._ibuffer)
        self._ibuffer = ""

        if type(dict()) == type(data) and data.has_key('action'):
            [getattr(self, n)(data) for n in ('Network_' + data['action'],
             'Network') if hasattr(self, n)]
        else:
            print "OOB data:", data

    def Pump(self):
        [asynchat.async_chat.push(self, d) for d in self.sendqueue]
        self.sendqueue = []

    def Send(self, data):
        """Returns the number of bytes sent after enoding."""

        data['PID'] = id.next()

        outgoing = dumps(data) + self.endchars
        self.sendqueue.append(outgoing)
        return len(outgoing)

    def handle_connect(self):
        if hasattr(self, "Connected"):
            self.Connected()
        else:
            print "Unhandled Connected()"

    def handle_error(self):
        #ignore EWOULDBLOCK
        if sys.exc_info()[1][0] == EWOULDBLOCK:
            return
            
        try:
            self.close()
        except:
            pass
        if hasattr(self, "Error"):
            self.Error(sys.exc_info()[1])
        else:
            asynchat.async_chat.handle_error(self)

    def handle_expt(self):
        pass

    def handle_close(self):
        if hasattr(self, "Close"):
            self.Close()
        asynchat.async_chat.handle_close(self)


