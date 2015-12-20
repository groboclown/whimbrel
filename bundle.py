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
import types
from distutils.dir_util import copy_tree

CONVERT_FILE_EXT = (".sh", ".py")
EXEC_FLAG_EXT = (".sh", ".py")
EXEC_FLAG_NAMES = list()
SKIP_EXT = (".pyc",)


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


def run_python_func(python_file, func_name, config):
    if os.path.isfile(python_file):
        with open(python_file, "r") as f:
            text = f.read() + "\n"
        config_compiled = compile(text, python_file, "exec", dont_inherit=True)
        config_module = types.ModuleType(os.path.basename(python_file), os.path.basename(python_file))
        exec(config_compiled, config_module.__dict__)
        if hasattr(config_module, func_name) and callable(getattr(config_module, func_name)):
            getattr(config_module, func_name)(config)
        else:
            raise Exception("Python file {0} has no function definition named `{1}'".format(python_file, func_name))


# =====================================================================================================

TARGETS = {}
RAN_TARGETS = []


def target(*deps):
    def x(code):
        def y(config):
            assert isinstance(config, Cfg)

            global RAN_TARGETS

            for d in deps:
                if d.__name__ not in RAN_TARGETS:
                    d(config)
            RAN_TARGETS.append(code.__name__)
            config.out.action("Target", code.__name__)
            try:
                code(config)
                config.out.status("PASS")
            except:
                config.out.status("FAIL")
                raise
        TARGETS[code.__name__] = x
        y.__name__ = code.__name__
        return y
    return x


class Cfg:
    def __init__(self):
        self.basedir = os.path.dirname(sys.argv[0])
        if self.basedir is None or self.basedir == '':
            self.basedir = os.path.curdir

        # Reuse the nice output code that's in the installer.
        sys.path.append(self.src("installer", "whimbrel", "install"))
        from util import out
        self.out = out

        self.distdir = self.src('dist')

    def src(self, *path):
        return os.path.join(self.basedir, *path)

    def dist(self, *path):
        return os.path.join(self.distdir, *path)

    def target(self, name):
        TARGETS[name](self)


def mk_config():
    return Cfg()


# =====================================================================================================
# =====================================================================================================
# =====================================================================================================

@target()
def clean(config):
    if os.path.isdir(config.distdir):
        shutil.rmtree(config.distdir)


# =====================================================================================================

@target()
def init(config):
    mkdir(config.distdir)


# =====================================================================================================

@target(init)
def docs(config):
    copy_tree(config.src('docs'), config.dist('docs'), False, None)


# =====================================================================================================

@target(init)
def installer(config):
    copy_tree(config.src("installer"), config.dist("installer"))
    fix_dir(config.dist("installer"), line_endings=True)
    set_exec_flag(config.dist("installer", "setup.py"))
    # TODO remove ignored extensions


# =====================================================================================================

@target(init)
def services(config):
    copy_tree(config.src("services"), config.dist("services"))
    fix_dir(config.dist("services"), line_endings=True, exec_flag=True)


# =====================================================================================================

@target(init)
def modules(config):
    copy_tree(config.src("modules"), config.dist("modules"))
    fix_dir(config.dist("modules"), line_endings=True, exec_flag=True)


# =====================================================================================================

@target(docs, installer, services, modules)
def bundle(config):
    pass


# =====================================================================================================

@target(bundle)
def lambdas(config):
    config.out.outln("")
    subprocess.call([config.dist("installer", "setup.py"), "setup.config", "bundle-lambdas", "nodejs-test"])


# =====================================================================================================

@target(lambdas)
def integration_tests(config):
    for module_name in os.listdir(config.basedir):
        test_dir = os.path.join(config.basedir, module_name, 'tests')
        if os.path.isdir(test_dir):
            for test_suite_name in os.listdir(test_dir):
                exec_file = os.path.join(test_dir, test_suite_name, 'exec.py')
                run_python_func(exec_file, 'execute', config)


# =====================================================================================================

@target(bundle, lambdas, integration_tests)
def all(config):
    pass


# =====================================================================================================

if __name__ == '__main__':
    cfg = mk_config()
    if len(sys.argv) <= 1:
        all(cfg)
    else:
        for arg in sys.argv[1:]:
            TARGETS[arg](cfg)
