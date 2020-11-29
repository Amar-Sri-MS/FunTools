#!/usr/bin/env python3

#
# Extracting archives
#

import os
import tarfile
import zipfile

from pathlib import Path


def extract(path):
    """ Extract archive in the exisiting path """
    if not os.path.exists(path):
        print('Archive does not exist')
        return

    if path.endswith('.zip'):
        opener, mode = zipfile.ZipFile, 'r'
    elif path.endswith('.tar'):
        opener, mode = tarfile.open, 'r:'
    elif path.endswith(('.tar.gz', '.tgz')):
        opener, mode = tarfile.open, 'r:gz'
    elif path.endswith(('.tar.bz2', '.tbz', '.tbz2', '.tz2', '.tb2', '.bz2')):
        opener, mode = tarfile.open, 'r:bz2'
    elif path.endswith(('.tar.lzma', '.tlz')):
        opener, mode = tarfile.open, 'r:xz'
    else:
        raise ValueError(f'Unsupported format archive: {path}')

    # Get current working directory
    cwd = os.getcwd()

    archive_path = os.path.splitext(path)[0]
    archive_name = os.path.basename(archive_path)
    print('Name of the archive:', archive_name)

    try:
        archive = opener(path, mode)

        # List of contents in the archive
        contents = list()
        # Whether the archive already contains a top level directory
        # with same name as the archive.
        # Need to create a folder if the archive does not have a top
        # level directory.
        dir_exists = False
        if type(archive) == zipfile.ZipFile:
            print('Type of archive: zip')
            contents = archive.infolist()
            dir_exists = len(contents) > 0 and contents[0].is_dir() and contents[0].filename == archive_name
        elif type(archive) == tarfile.TarFile:
            print('Type of archive: tar')
            contents = archive.getmembers()
            dir_exists = len(contents) > 0 and contents[0].isdir() and contents[0].name == archive_name

        if dir_exists:
            parent_path = Path(archive_path).parent
            os.chdir(parent_path)
            print('Extracting archive at parent', parent_path)
        else:
            # Change to the directory where the archive needs to be extracted
            os.makedirs(archive_path, exist_ok=True)
            os.chdir(archive_path)
            print('Extracting archive at', archive_path)

        archive.extractall()
    except Exception as e:
        print('Could not extract archive, Reason:', e)
    finally:
        # Close the archive file opener
        if archive:
            archive.close()
        # Change back to the working directory
        os.chdir(cwd)


def is_archive(path):
    """ Check if the file at the path is an archive """
    if os.path.isdir(path):
        return False
    if tarfile.is_tarfile(path) or zipfile.is_zipfile(path):
        return True
    return False