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
            'system_type': msg_tuple[2],
            'system_id': msg_tuple[3],
            'uid': msg_tuple[4],
            'display_time': msg_tuple[5],
            'level': msg_tuple[6],
            'line': msg_tuple[7]
            }

def lines_to_iterable(lines):
    iter = [(None, None, None, None, 'uid', None, None, line) for line in lines]
    return iter