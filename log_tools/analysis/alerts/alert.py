#!/usr/bin/env python3

#
# Base definition of an alert type.
# Different types of alerting can be creating using
# this class.
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2022 Fungible Inc.  All rights reserved.

class AlertType(object):
    """
    Base definition of an alert type for alerting.
    """

    def process(self, alert):
        """
        Takes input dict, sends alert using it.

        Dict should contain the following keys:
        - context_title (str)
        - context_message (str)
        - tags (list)
        - hits
        """
        raise NotImplementedError()

    def set_config(self, config):
        """ Sets the config for this alert """
        pass