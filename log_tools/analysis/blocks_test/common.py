#
# Common utilities across test code.
#

def process(block, iter):
    """
    Wraps the process function to assume single input iterable and
    a list output for simple unit testing.
    """
    output_iter = block.process([iter])
    return list(output_iter)


def msg_tuple_to_dict(msg_tuple):
    """
    Convert the tuple that we use to communicate between blocks
    into a dict for readable access in tests.
    """
    return {'datetime': msg_tuple[0],
            'usecs': msg_tuple[1],
            'uid': msg_tuple[2],
            'display_time': msg_tuple[3],
            'line': msg_tuple[4]
            }

def lines_to_iterable(lines):
    iter = [(None, None, 'uid', None, line) for line in lines]
    return iter