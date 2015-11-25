#!/usr/bin/python

"""
Constructs the basic bundles for use.
"""


import os
import sys
import shutil
from distutils.dir_util import copy_tree

SIMPLE_JOIN = [
    'simple-client-api/activity-exec-update',
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
            out.action("Copy", " -> {0} to {1}".format(src_dir, dest_dir))
            copy_tree(src_dir, dest_dir)
            out.status("OK")

    for join_dir in SIMPLE_JOIN:
        base_dir = os.path.join(basedir, join_dir)
        dest_dir = os.path.join(export_dir, join_dir)
        for f in os.listdir(base_dir):
            src_dir = os.path.join(base_dir, f)
            fd_dir = os.path.join(dest_dir, f)
            out.action("Copy", "Setting up {0}: {1} to {2}".format(join_dir, src_dir, fd_dir))
            copy_tree(src_dir, fd_dir)
            out.status("OK")
            src_dir = os.path.join(basedir, 'whimbrel-client-core', f)
            out.action("Copy", "Setting up {0}: {1} to {2}".format(join_dir, src_dir, fd_dir))
            copy_tree(src_dir, fd_dir)
            out.status("OK")
