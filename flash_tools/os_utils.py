'''
Copyright (c) 2019-2020 Fungible, inc.
All Rights Reserved.
'''

import os
import platform
import subprocess

def path_fixup(app):
    # if running on Linux then the app is expected to be in $PATH
    # if running on Darwin then the app is expected to be in $PATH or provided by brew
    known_apps = {
        'mkfs.ext4': { 'check_args': '-V', 'brew_package': 'e2fsprogs', 'brew_path':'sbin' },
        'sfdisk' :   { 'check_args': '-v', 'brew_package': 'util-linux', 'brew_path':'sbin' },
        'makeself' : { 'check_args': '-v', 'brew_package': 'makeself', 'brew_path':'bin' }
    }
    try:
        subprocess.check_call([ app, known_apps[app]['check_args'] ])
        return app
    except:
        if platform.system() == 'Linux':
            raise 'App {} not found'

    try:
        path = subprocess.check_output(['brew', '--prefix', known_apps[app]['brew_package']])
        full_app = os.path.join(path.strip(), known_apps[app]['brew_path'], app)
        subprocess.check_call([ full_app, known_apps[app]['check_args'] ])
        return full_app
    except:
        raise 'App {} not found. Install it with "brew install {}"'

