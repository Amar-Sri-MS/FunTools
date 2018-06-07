import glob
import os
import resource
import shutil
import subprocess
import sys
import time

class Filer():
    def __init__(self):
        pass

    def __rmdir(self, dirname):
        if os.path.exists(dirname):
            if os.path.isdir(dirname):
                shutil.rmtree(dirname)

    def __rmfile(self, dirname):
        if os.path.exists(dirname):
            if os.path.isfile(dirname):
                os.remove(dirname)

    def mkdir(self, dirname, rm=False):
        if rm:
            self.__rmdir(dirname)
        self.__rmfile(dirname)
        if not os.path.exists(dirname):
            os.makedirs(dirname)


class Compiler():
    def __init__(self):
        pass
    def clean_files(self, f_lst):
        pass
    def __compile(self, call):
            print "Compiling: {}".format(' '.join(elem for elem in call))
            p = subprocess.Popen(call, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            while True:
                output = p.stdout.readline()
                if output == '' and p.poll() is not None:
                    break
                sys.stdout.write(output)
                sys.stdout.flush()
            if p.returncode != 0:
                output = p.communicate()[0]
                raise ProcessException(call_str, p.returncode, output)
            return
    def build_lib(self, libname, libtype,
            src_f_lst, inc_dir, out_lib_dir, out_inc_dir):

        # Prepare list of include directories
        inc_path = []
        for path in inc_dir:
            inc_path.extend(["-I", path])
        compiler = os.getenv("CXX", None)
        assert compiler != None, "No compiler specified for compilation"
        compile_call = [compiler,"-std=c++11", "-Wall", "-v"] + inc_path

        if libtype.lower() == "shared":
            l_obj = "{}.so".format(libname)
            compile_call.append("-fPIC")
            lib_call = [compiler, "-o", l_obj, "-fPIC", "-shared"]
        else:
            l_obj = "{}.a".format(libname)
            lib_call = ["ar", "cr", l_obj]

        obj_files = []

        for src_f in src_f_lst:
            obj_file_arr = os.path.basename(src_f).split('.')[:-1]
            obj_file = ".".join(n for n in obj_file_arr)
            obj_file = "{}.o".format(obj_file)
            n_call = compile_call + ["-c", src_f]
            self.__compile(n_call)
            obj_files.append(obj_file)

        lib_call.extend(obj_files)
        self.__compile(lib_call)

        # Now remove all the object files
        for obj_f in obj_files:
            print "Removing: {}".format(obj_f)
            os.remove(obj_f)

        #Copy over all the include files
        curr_dir = os.path.abspath(os.path.curdir)
        for dirname in inc_dir:
            if dirname == curr_dir:
                continue
            for f_name in os.listdir(dirname):
                if f_name.endswith(".h"):
                    print "Installing:{}/{} ".format(out_inc_dir, f_name)
                    shutil.copy(os.path.join(dirname, f_name), out_inc_dir)

        if out_lib_dir == curr_dir:
            return
        #Copy over the library
        print "Installing {} lib to {}".format(l_obj, out_lib_dir)
        shutil.copy(l_obj, out_lib_dir)
        os.remove(l_obj)
