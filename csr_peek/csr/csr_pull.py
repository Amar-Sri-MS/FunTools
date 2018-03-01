#
#  csr_pull.py
#
#  Created by Hariharan Thantry on 2018-03-01
#
#  Copyright 2018 Fungible Inc. All rights reserved.
#

import glob
import os
import shutil
import subprocess

class CSRPull():
    HOST='10.1.20.59'
    PATH='/csr'
    DIRS=['inc']
    FILE_EXT=['*.yaml']
    FILES=['ringAN.yaml', 'AMAP']

    def __init__(self, dst_dir):

        self.__check_dir(dst_dir)

        #mnt_dir = "/tmp/csr.{}".format(os.getpid())
        #self.__rm_dir(mnt_dir)
        #os.mkdir(mnt_dir)
        #self.__mount_dir(mnt_dir)

        #TODO: Remove after mounts available
        mnt_dir = "/tmp/csr.19"

        src_dir = os.path.join(mnt_dir, "f1", "gen")
        self.__copy(dst_dir, src_dir)

    def __mount_dir(self, mnt_dir):
        mnt_str = "mount -t nfs {}:{} {}".format(CSRPull.HOST, CSRPull.PATH, mnt_dir)
        subprocess.check_call(mnt_str, shell=True)

    def __check_dir(self, dirname):
        if not os.path.exists(dirname):
            assert False, "{} does not exist".format(dirname)
        if not os.path.isdir(dirname):
            assert False, "{} not a directory".format(dirname)

    def __rm_dir(self, mnt_dir):
        if os.path.exists(mnt_dir):
            if os.path.isdir(mnt_dir):
                shutil.rmtree(mnt_dir)
            if os.path.isfile(mnt_dir):
                os.remove(mnt_dir)

    def __copy(self, dst_dir, src_dir):
        # First the files
        for fname in CSRPull.FILES:
            src_f = os.path.join(src_dir, fname)
            shutil.copy(src_f, dst_dir)
        # Next the directory
        for dirname in CSRPull.DIRS:
            n_dst=os.path.join(dst_dir, dirname)
            n_src = os.path.join(src_dir, dirname)
            self.__copy_files(n_dst, n_src)
    def __copy_files(self, dst_dir, src_dir):
        
        if not os.path.exists(dst_dir):
            os.mkdir(dst_dir)

        for file_ext in CSRPull.FILE_EXT:
            for act_file in glob.glob(os.path.join(src_dir, file_ext)):
                shutil.copy(act_file, dst_dir)






