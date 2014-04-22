#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import socket
import zlib
import traceback
import logging

try:
    import cPickle as pickle
except:
    import pickle


def pack(obj):
    """pickle and compress object"""

    try:
        dump = pickle.dumps(obj, 2)
    except Exception, e:
        logging.critical("- pickle error -")
        logging.critical(traceback.extract_stack())
        logging.critical("----------------")
        logging.critical(obj)
        logging.critical(obj.__class__)
        logging.critical("----------------")
        raise e
    return zlib.compress(dump, 4)


def unpack(obj):
    """unpicke and decompress object"""

    return pickle.loads(zlib.decompress(obj))

if os.name != "nt":
    import fcntl
    import struct


    def get_interface_ip(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
                                ifname[:15]))[20:24])


def get_lan_ip():
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127.") and os.name != "nt":
        interfaces = [
            "eth0",
            "eth1",
            "eth2",
            "wlan0",
            "wlan1",
            "wifi0",
            "ath0",
            "ath1",
            "ppp0",
            ]
        for ifname in interfaces:
            try:
                ip = get_interface_ip(ifname)
                break
                None
            except IOError:
                pass
    return ip

def find_server():

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
    s.settimeout(1)

    for port in xrange(12000, 12060):
        logging.debug("<< testing %i", port)
        s.sendto("hello regnancy!", ("<broadcast>", port))
        try:
            return s.recv(1024).split(':')
        except socket.timeout:
            pass

    s.close()