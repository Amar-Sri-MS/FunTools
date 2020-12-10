class Block(object):
    """
    Base definition of a block in the analysis pipeline.
    """

    def process(self, iters):
        """
        Takes input iterables, produces output iterable.

        Iterable elements must be a standard 8-tuple:
        (datetime object, time_usecs, system_type, system_id, source_uid, display_time, level, message)

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