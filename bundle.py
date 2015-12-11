#!/usr/bin/python

"""
Constructs the basic bundles for use.
"""

import os
import shutil
import stat
import sys
import tempfile
import subprocess
from distutils.dir_util import copy_tree

CONVERT_FILE_EXT = (".sh", ".py")
EXEC_FLAG_EXT = (".sh", ".py")
EXEC_FLAG_NAMES = list()


def _copy_to_temp_file_with_fix_line_endings(filename):
    (src_handle, src_name) = tempfile.mkstemp()
    try:
        with open(filename, "rb") as f:
            data = f.read()
            data = data.replace(b"\r\n", b"\n")
        os.write(src_handle, data)
        os.close(src_handle)
    except:
        os.close(src_handle)
        os.unlink(src_name)
        raise
    return src_name


def fix_line_endings(filename):
    temp_file = _copy_to_temp_file_with_fix_line_endings(filename)
    try:
        shutil.move(temp_file, filename)
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def set_exec_flag(filename):
    st = os.stat(filename)
    os.chmod(filename, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def fix_dir(dir_name, line_endings=False, exec_flag=False):
    for (path, dirs, files) in os.walk(dir_name):
        for name in files:
            file = os.path.join(path, name)
            ext = os.path.splitext(name)[1]
            if line_endings and ext in CONVERT_FILE_EXT:
                fix_line_endings(file)
            if exec_flag and (ext in EXEC_FLAG_EXT or name in EXEC_FLAG_NAMES):
                set_exec_flag(file)


def mkdir(filename):
    if not os.path.isdir(filename):
        os.makedirs(filename)


# =====================================================================================================


if __name__ == '__main__':
    # INIT
    basedir = os.path.dirname(sys.argv[0])
    if basedir is None or basedir == '':
        basedir = os.path.curdir
    sys.path.append(os.path.join(basedir, "installer", "whimbrel", "install"))
    from util import out
    dist_dir = os.path.join(basedir, 'dist')

    # CLEAN
    if os.path.isdir(dist_dir):
        shutil.rmtree(dist_dir)

    # MK-DIST
    mkdir(dist_dir)

    # MK-DOCS
    out.action("Copy", "docs")
    copy_tree(os.path.join(basedir, 'docs'), os.path.join(dist_dir, 'docs'), False, None)
    out.status("OK")

    # MK-INSTALLER
    out.action("Make", "installer")
    copy_tree(os.path.join(basedir, "installer"), os.path.join(dist_dir, "installer"))
    fix_dir(os.path.join(dist_dir, "installer"), line_endings=True)
    set_exec_flag(os.path.join(dist_dir, "installer", "setup.py"))
    out.status("OK")

    # MK-SERVICES
    out.action("Make", "services")
    copy_tree(os.path.join(basedir, "services"), os.path.join(dist_dir, "services"))
    fix_dir(os.path.join(dist_dir, "services"), line_endings=True, exec_flag=True)
    out.status("OK")

    # MK-MODULES
    out.action("Make", "modules")
    for module_name in os.listdir(os.path.join(basedir, "modules")):
        # A bit tricky...
        module_dir = os.path.join(basedir, "modules", module_name)
        if os.path.isfile(module_dir):
            mkdir(os.path.join(dist_dir, "modules"))
            shutil.copyfile(module_dir, os.path.join(dist_dir, "modules", module_name))
            continue
        if os.path.isdir(os.path.join(module_dir, "installer", "python2_3", "module_" + module_name)):
            copy_tree(
                os.path.join(module_dir, "installer", "python2_3", "module_" + module_name),
                os.path.join(dist_dir, "installer", "module_" + module_name),
                False, None)
        else:
            raise Exception("No installer for module " + module_name)

    copy_tree(os.path.join(basedir, "modules"), os.path.join(dist_dir, "modules"))
    out.status("OK")

    # INITIAL MK-LAMBDAS (for quick test execution)
    subprocess.call([os.path.join(dist_dir, "installer", "setup.py"), "setup.config", "lambdas"])
