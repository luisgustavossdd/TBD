#!/usr/bin/python
# -*- coding: utf-8 -*-

class InfoToken(object):
    
    def __init__(self, text, *args, **kwargs):
        assert text
        self.text = text
        for k in kwargs:
            self.__dict__[k] = kwargs[k]
        
    def __str__(self):
        return self.text
    
    def __repr__(self):
        return self.text