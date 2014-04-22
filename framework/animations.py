#!/usr/bin/python
# -*- coding: utf-8 -*-


def move_linear(old, new, speed=25, finalfunc=None):
    while old != new:
        yield old
        if old > new:
            old -= min(speed, old - new)
        elif old < new:
            old += min(speed, new - old)
    if finalfunc:
        finalfunc()
    else:
        while True:
            yield old


