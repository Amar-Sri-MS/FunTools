class Block(object):
    """
    Base definition of a block in the analysis pipeline.
    """

    def process(self, iters):
        """
        Takes input iterables, produces output iterable.

        Iterable elements must be a standard 8-tuple:
        (datetime object, time_usecs, system_type, system_id, source_uid, display_time, level, message)

        system_type: Type of system that generated the log lines.
        (Possible values: fs1600, controller, cluster)

        system_id: Unique identifer of the system that generated the logs.
        (Possible values: MAC address for fs1600 system, Node ID in case of cluster)

        source_uid: Refers to the software element that generated the logs.
        (Possible values: apigateway, dataplacement, funos, storage_agent)

        The tuple is our poor man's version of a structured log.

        Input blocks will ignore iters, output blocks will return None.
        """
        raise NotImplementedError()

    def set_config(self, config):
        """ Sets the config for this block """
        pass

    def tuple_to_dict(self, tuple):
        """
        Convert the tuple that we use to communicate between blocks
        into a dict
        """
        return {'datetime': tuple[0],
                'usecs': tuple[1],
                'system_type': tuple[2],
                'system_id': tuple[3],
                'uid': tuple[4],
                'display_time': tuple[5],
                'level': tuple[6],
                'line': tuple[7]
                }