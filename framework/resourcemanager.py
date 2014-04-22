#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
from os.path import basename, splitext, join
from collections import defaultdict
from pygame.resourcehandling import LazyImageLoader
from pygame.resourcehandling import get_default_image
    
class ResourceManager(object):

    def __init__(self):
        self.cache = defaultdict(get_default_image)
        self.key_prepare_pattern = re.compile( '(\W|-)')
    
    def get(self, key, suffix=None):
        prepared_key = self.key_prepare_pattern.sub('', key)
        return (self.cache)[prepared_key](suffix)

    def load(self, fullpath, size, modifier):
        if not modifier:
            modifier = {}
            
        filename = splitext(basename(fullpath))[0]
        key = filename.split('_')[0]
        
        # add empty modifier for e.g. anvil_ico => will be called as 'anvil', 'ico'
        for subkey in filename.split('_'):
            modifier[subkey]= lambda y: y
        
        (self.cache)[key] = LazyImageLoader(fullpath, modifier, size)
        
    def load_images(self, path, size, modifier=None, extensions='.png;.jpg'):
        extensions = filter(None, extensions.split(';'))
            
        files = [f for f in os.listdir(path) if splitext(f)[1] in extensions]
        for f in files:
            fullpath = join(path, f)
            self.load(fullpath, size, modifier)
            
            


