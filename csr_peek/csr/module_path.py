#!/usr/bin/env python3

import os
import sys
import inspect

class module_locator():
    def __init__(self):
        self.is_frozen = hasattr(sys, "frozen")
        self.encoding = sys.getfilesystemencoding()

    def module_path(self):
       if self.is_frozen:
           return os.path.dirname(sys.executable)
       return os.path.dirname(__file__)

    def curr_path(self):
       return os.environ.get('OLDPWD')
