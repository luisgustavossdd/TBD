#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import server.regnancyserver

try:
    import psyco
    psyco.full()
except:
    pass

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print "Missing port number."
        print "Usage:"
        print "  python start_server.py 9989"
        sys.exit()
    
    port = (sys.argv)[1]
    s = server.regnancyserver.RegnancyServer(port=int(port))
    
    s.Launch()
