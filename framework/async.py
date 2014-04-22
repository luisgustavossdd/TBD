#!/usr/bin/python
# -*- coding: utf-8 -*-

from multiprocessing import Process, Pipe
import platform

class CancelToken(object):
    def __init__(self):
        self.cancel = False

PP_QUIT = "QUIT"
PP_KEEP_ALIVE = "KEEP_ALIVE"

def get_timeout_pipe(pipe):
    return TimeOutPipe(pipe) if pipe else DummyTimeOutPipe()

class TimeOutPipe(object):
    
    def __init__(self, pipe, timeouttoken=None):
        self.pipe = pipe
        self.__timeouttoken = timeouttoken or TimeOutToken()

    def send(self, *args):
        self.pipe.send(*args)

    def check(self):
        return self.__timeouttoken.check_pipe_timeout(self.pipe)

class DummyTimeOutPipe(TimeOutPipe):
    
    def __init__(self, *args):
        pass
    
    def check(self):
        return True
    
    def send(self, *args):
        pass
    
class TimeOutToken(object):
    
    def __init__(self, pushlimit=20000):
        self.__deathcounter = 0
        self.__pushlimit = 20000
        
    def reset(self):
        self.__deathcounter = 0
        
    def push(self):
        self.__deathcounter += 1
        return self.__deathcounter < self.__pushlimit

    def check_pipe_timeout(self, pipe):
        if pipe.poll(0.01):
            self.reset()
            return not PP_QUIT in pipe.recv()
        
        return self.push()

class ProcessProxy(object):

    """Encapsulates a Process and a Pipe to run a function asynchronous"""

    def __init__(self, function):
        assert function
        assert hasattr(function, '__call__')

        self.function = function
        self.started = False
        self.joined = False
        self.pipe = None
        self.process = None
        self.shuttingdown = False

    def start(self):
        """Start a Process with the given function"""

        (self.pipe, child_pipe) = Pipe()

        if platform.system() == "Windows":  # Maybe use polymorphism instead...
            from threading import Thread
            self.process = Thread(None, self.function, None, (child_pipe,))
        else:
            self.process = Process(target=self.function, args=(child_pipe,))

        self.process.start()
        self.started = True

    def join(self):
        """Tell the Process to exit and wait for it"""

        assert self.started

        try:
            self.pipe.send([PP_QUIT])
        except:
            pass

        self.process.join()
        self.joined = True

    def poll(self):
        if self.pipe.poll(2):
            return self.pipe.recv()
        raise Exception

    def keep_alive(self, debug=False):
        """Send a keep-alive message to the Process and listen for a Quit command"""

        assert self.started
        if self.shuttingdown or self.joined:
            return False
        if self.pipe.poll(0.01):
            cmd = self.pipe.recv()
            if PP_QUIT in cmd:
                self.shuttingdown = True
                self.process.join()
                self.joined = True
                self.pipe.close()
                return False
        else:
            self.pipe.send([PP_KEEP_ALIVE])
            return True


