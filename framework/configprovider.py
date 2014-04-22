#!/usr/bin/python
# -*- coding: utf-8 -*-

import platform
import os
import errno


class ConfigProvider(object):

    def __init__(self):

        system = platform.system()

        if system == "Windows":
            base = os.getenv("APPDATA")
        else:
            try:
                from xdg.BaseDirectory import xdg_data_home
                base = xdg_data_home
            except:
                base = os.path.join(os.path.expanduser("~user"),
                                    ".local", "share")

        config_dir = os.path.join(base, "Regnancy")

        self.__ensure(config_dir)

        self.config_dir = config_dir

    def write(self, filename, text):
        with open(os.path.join(self.config_dir, filename), 'w') as f:
            f.write(text)

    def read(self, filename):
        with open(os.path.join(self.config_dir, filename), 'r') as f:
            return f.readlines()

    def __ensure(self, path):
        try:
            os.makedirs(path)
        except OSError, e:
            if e.errno != errno.EEXIST:
                raise

    def get_files(self, folder):
        path = os.path.join(self.config_dir, folder)
        self.__ensure(path)
        return os.listdir(path)


