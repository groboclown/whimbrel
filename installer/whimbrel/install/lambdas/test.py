
import os
import subprocess
import types
from ..cfg import Config
from ..util import out
from .bundle import get_lambda_basedir

TEST_TYPES = ('integration-tests', 'unit-tests')

def test_lambdas(config):
    assert isinstance(config, Config)
    for test_name, test_file in _find_tests(config).items():
        _run_test(test_name, test_file, config)




def _find_tests(config):
    assert isinstance(config, Config)
    lambda_basedir = get_lambda_basedir(config)
    tests = {}
    for lambda_name in os.listdir(lambda_basedir):
        location = os.path.join(lambda_basedir, lambda_name)
        if os.path.isdir(location):
            if lambda_name not in tests or not os.path.isfile(tests[lambda_name]) and _has_test_dirs(location):
                tests[lambda_name] = location
        elif os.path.splitext(lambda_name)[1] == '.py' and lambda_name[:5] == "test_":
            name = os.path.splitext(lambda_name)[0][5:]
            tests[name] = location
    return tests


def _run_test(test_name, test_file, config):
    if os.path.isdir(test_file):
        for test_type in TEST_TYPES:
            location = os.path.join(test_file, test_type)
            if os.path.isdir(location):
                _run_mocha_test_dir(test_name + "/" + test_type, location, config)
    else:
        _run_python_test_file(test_name, test_file, config)


def _run_mocha_test_dir(test_name, test_dir, config):
    out.action("Test", test_name)

    _setup_test(test_dir, config)

    proc = subprocess.Popen(
            [config.node_exec, "node_modules/mocha/bin/mocha", "test/*Test.js"],
            cwd=test_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=-1)
    returncode, stdout, stderr = _pump_output(proc)
    if returncode != 0:
        out.status("FAILED")
        out.outln("Stdout:")
        out.outln(stdout)
        out.outln("Stderr:")
        out.outln(stderr)
    else:
        out.status("PASSED")

    _teardown_test(test_dir, config)


def _run_python_test_file(test_name, test_file, config):
    out.action("Test", test_name)

    # FIXME

    out.status("NOT RUN")


def _has_test_dirs(file):
    for test_type in TEST_TYPES:
        if os.path.isdir(os.path.join(file, test_type)):
            return True
    return False


def _pump_output(proc):
    assert isinstance(proc, subprocess.Popen)
    stdout = ""
    stderr = ""
    while True:
        if proc.poll() is not None:
            stdout += proc.stdout.read()
            stderr += proc.stderr.read()
            return [proc.returncode, stdout, stderr]
        stdout += proc.stdout.read()
        stderr += proc.stderr.read()


def _setup_test(test_dir, config):
    _run_python_func(os.path.join(test_dir, "setup.py"), "setup", config)


def _teardown_test(test_dir, config):
    _run_python_func(os.path.join(test_dir, "teardown.py"), "teardown", config)


def _run_python_func(python_file, func_name, config):
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
