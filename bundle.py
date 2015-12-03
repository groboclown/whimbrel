#!/usr/bin/python

"""
Constructs the basic bundles for use.
"""


import os
import sys
import shutil
import tempfile
import stat
from distutils.dir_util import copy_tree

SIMPLE_JOIN = [
    'simple-client-api/activity-update',
    'simple-client-api/heartbeat',
    'simple-client-api/request-workflow-exec',
    'lambda-source'
]
COPY = [
    'installer'
]
JOIN = {
    'services/heartbeat-monitor': [],
    'services/web-monitor': []
}
CONVERT_FILE_EXT = (".sh", ".py")
EXEC_FLAG_EXT = (".sh", ".py")
EXEC_FLAG_NAMES = list()


def _copy_to_temp_file_with_fix_line_endings(filename):
    (src_handle, src_name) = tempfile.mkstemp()
    try:
        with open(filename, "rb") as f:
            os.write(src_handle, f.read().replace("\r\n", "\n"))
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


if __name__ == '__main__':
    basedir = os.path.dirname(sys.argv[0])
    if basedir is None or basedir == '':
        basedir = os.path.curdir
    sys.path.append(os.path.join(basedir, "installer", "python2_3"))
    from whimbrel.install.util import out
    export_dir = os.path.join(basedir, 'dist')
    if os.path.isdir(export_dir):
        shutil.rmtree(export_dir)
    os.makedirs(export_dir)

    for copy_dir in COPY:
        src_dir = os.path.join(basedir, copy_dir)
        dest_dir = os.path.join(export_dir, copy_dir)
        out.action("Copy", "Setting up {0}: {1} to {2}".format(copy_dir, src_dir, dest_dir))
        copy_tree(src_dir, dest_dir, False, None)
        out.status("OK")

    for join_dir, core_dirs in JOIN.items():
        src_dir = os.path.join(basedir, join_dir)
        dest_dir = os.path.join(export_dir, join_dir)
        out.action("Copy", "Setting up {0}: {1} to {2}".format(copy_dir, src_dir, dest_dir))
        copy_tree(src_dir, dest_dir)
        out.status("OK")

        for core_dir in core_dirs:
            src_dir = os.path.join(basedir, 'whimbrel-client-core', core_dir)
            copy_tree(src_dir, dest_dir)

    for join_dir in SIMPLE_JOIN:
        base_dir = os.path.join(basedir, join_dir)
        dest_dir = os.path.join(export_dir, join_dir)
        out.action("Copy", "Setting up {0}".format(join_dir))
        for f in os.listdir(base_dir):
            src_dir = os.path.join(base_dir, f)
            fd_dir = os.path.join(dest_dir, f)
            copy_tree(src_dir, fd_dir)
            src_dir = os.path.join(basedir, 'whimbrel-client-core', f)
            copy_tree(src_dir, fd_dir)
        out.status("OK")

    out.action("Fix", "Fixing line endings and exec flags")
    for (path, dirs, files) in os.walk(export_dir):
        for f in files:
            file = os.path.join(path, f)
            ext = os.path.splitext(f)[1]
            if ext in CONVERT_FILE_EXT:
                fix_line_endings(file)
            if ext in EXEC_FLAG_EXT or f in EXEC_FLAG_NAMES:
                set_exec_flag(file)
    out.status("OK")
