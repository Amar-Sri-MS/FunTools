#!/usr/bin/env python3

#
# Custom Exceptions
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2022 Fungible Inc.  All rights reserved.


class EmptyPipelineException(Exception):
    pass

class NotFoundException(Exception):
    pass

class NotSupportedException(Exception):
    pass