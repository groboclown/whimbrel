
import os
import subprocess
from ..cfg import Config
from ..util import out
from .bundle import get_node_test_basedir, load_package_file


def test_nodejs(config):
    assert isinstance(config, Config)
    test_basedir = get_node_test_basedir(config)
    for module_name in os.listdir(test_basedir):
        module_test_dir = os.path.join(test_basedir, module_name)
        for node_package_name in os.listdir(module_test_dir):
            node_package_dir = os.path.join(module_test_dir, node_package_name)
            _run_nodejs_tests(config, node_package_name, node_package_dir)


def _run_nodejs_tests(config, node_name, node_package_dir):
    package = load_package_file(node_package_dir)
    if package is not None:
        if "scripts" in package and "test" in package["scripts"]:
            out.action("Test", node_name)

            # cmd = [config.node_exec, "node_modules/mocha/bin/mocha", "test/*Test.js"]
            # cmd = package["scripts"]["test"]
            cmd = [config.node_exec, "node_modules/mocha/bin/mocha", "test/*-test.js"]

            print("\ncmd: " + str(cmd))
            print("cwd: " + node_package_dir)

            proc = subprocess.Popen(
                    cmd,
                    executable=config.node_exec,
                    cwd=node_package_dir,
                    bufsize=-1)
            proc.wait()
            returncode = proc.returncode
            # proc = subprocess.Popen(
            #         cmd,
            #         executable=config.node_exec,
            #         cwd=node_package_dir,
            #         stdout=subprocess.PIPE,
            #         stderr=subprocess.PIPE,
            #         bufsize=-1)
            # returncode, stdout, stderr = _pump_output(proc)
            if returncode != 0:
                out.status("FAILED")
                out.outln("Stdout:")
                #out.outln(stdout)
                out.outln("Stderr:")
                #out.outln(stderr)
            else:
                out.status("PASSED")


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
