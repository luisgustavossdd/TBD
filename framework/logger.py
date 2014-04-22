#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging


def logcall(func):

    def _logcall(*args, **kw):
        logging.debug("%s.%s" % (args[0], func.__name__))
        return func(*args, **kw)

    return _logcall

