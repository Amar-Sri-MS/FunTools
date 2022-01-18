#!/usr/bin/env python2.7

import os
import sys
import inspect

class module_locator():
    def __init__(self):
        self.is_frozen = hasattr(sys, "frozen")
        self.encoding = sys.getfilesystemencoding()

    def module_path(self):
       if self.is_frozen:
           return os.path.dirname(unicode(sys.executable, self.encoding))
       return os.path.dirname(unicode(__file__, self.encoding))

    def curr_path(self):
       return os.environ.get('OLDPWD')
