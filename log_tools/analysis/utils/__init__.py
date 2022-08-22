import os


def is_file_readable(file_path):
    """ Check if the user has read permissions for the given file_path """
    return os.access(file_path, os.R_OK)