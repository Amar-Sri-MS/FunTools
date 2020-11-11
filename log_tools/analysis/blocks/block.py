class Block(object):
    """
    Base definition of a block in the analysis pipeline.
    """

    def process(self, iters):
        """
        Takes input iterables, produces output iterable.

        Iterable elements must be a standard 5-tuple:
        (datetime object, time_usecs, source_uid, display_time, message)

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
                'uid': tuple[2],
                'display_time': tuple[3],
                'line': tuple[4]
                }