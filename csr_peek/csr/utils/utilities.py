import glob
import os
import resource
import shutil
import shlex
import subprocess
import sys
import time

class Filer():
    def __init__(self):
        pass

    def __rmdir(self, dirname):
        if os.path.exists(dirname):
            if os.path.isdir(dirname):
                shutil.rmtree(dirname)

    def __rmfile(self, dirname):
        if os.path.exists(dirname):
            if os.path.isfile(dirname):
                os.remove(dirname)

    def mkdir(self, dirname, rm=False):
        if rm:
            self.__rmdir(dirname)
        self.__rmfile(dirname)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

