#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import client.pygameclient.pygameclient as pgc
import client.regnancyclient as rc
import game
import logging

try:
    import psyco
    psyco.full()
except:
    pass


logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser(description='Regnancy - the deck building game.')
parser.add_argument('-d', '--debug', action='store_true', help='run Regnancy in debug mode')
parser.add_argument('-p', '--port', action='store', help='always try to run servers on this port')
parser.add_argument('-n', '--name', action='store', nargs='+', help='sets the player name')
group = parser.add_mutually_exclusive_group()
group.add_argument('-j', '--join', action='store_true', help='join a running game immediately')
group.add_argument('-s', '--start', action='store_true', help='start a new game immediately')
group.add_argument('-q', '--quickmatch', action='store_true', help='start a new game immediately against an AI opponnent')

args = vars(parser.parse_args())

if __name__ == "__main__":
    game.global_options.debug_mode = args['debug']
    if args['port']:
        game.global_options.port = int(args['port'])
    name = " ".join(args['name']) if args['name'] else None
    client = pgc.PygameClient(name, args['start'], args['join'], args['quickmatch'])
    rc.RegnancyClient().run(client)
