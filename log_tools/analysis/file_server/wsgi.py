#!/usr/bin/env python3

#
# WSGI Entry Point for Gunicorn server to interact
# with the file server.
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

from server import app


if __name__ == '__main__':
    app.run()