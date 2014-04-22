#!/usr/bin/python
# -*- coding: utf-8 -*-


class LateCall(object):

    def __init__(self, f):
        self.f = f

    def __call__(self):
        self.f()


