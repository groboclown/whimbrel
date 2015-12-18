"""
Create the install bundles for the lambdas.
"""

import os
import subprocess
import json


def get_npm_cache_dir(config):
    return os.path.join(config.cache_dir, "npm_cache.d")


def npm_install(config, name):
    """
    Download an npm module to the npm cache directory.

    :param config:
    :param name:
    :return:
    """
    assert hasattr(config, "cache_dir")
    npm_cache_dir = get_npm_cache_dir(config)
    # Looks like dependencies are loaded inside the module itself...
    # So this doesn't need to worry about recursive dependencies.
    # deps = _get_npm_module_dependencies(config, name)
    deps = [name]
    module_install_dirs = []
    all_installed = True
    for dep in deps:
        dep_dir = os.path.join(npm_cache_dir, "node_modules", dep)
        if not os.path.isdir(dep_dir):
            all_installed = False
        module_install_dirs.append(dep_dir)
    if all_installed:
        return module_install_dirs
    if not os.path.isdir(npm_cache_dir):
        os.makedirs(npm_cache_dir)
    subprocess.check_call([config.npm_exec, "install", name], cwd=npm_cache_dir)
    for dep_dir in module_install_dirs:
        if not os.path.isdir(dep_dir):
            raise Exception("npm install did not create {0}".format(module_install_dirs))
    return module_install_dirs


def get_npm_module_dependencies(config, name, known_depends=None):
    """
    Load the JSon dictionary that describes the dependencies for a module.
    It will recursively search for dependencies.

    :param config:
    :param name:
    :param known_depends:
    :return:
    """
    assert hasattr(config, "cache_dir")
    npm_cache_dir = get_npm_cache_dir(config)
    if known_depends is None:
        known_depends = []
    found = [name]
    while len(found) > 0:
        dep_name = found.pop()
        if dep_name in known_depends:
            continue
        known_depends.append(dep_name)
        dep_file = os.path.join(get_npm_cache_dir(config), "{0}.dependencies.json".format(dep_name))
        if not os.path.isfile(dep_file):
            if not os.path.isdir(os.path.dirname(dep_file)):
                os.makedirs(os.path.dirname(dep_file))
            with open(dep_file, "w") as df:
                with open(os.devnull, "w") as devnull:
                    process = subprocess.Popen(
                            args=[config.npm_exec, "view", "--json", dep_name, "dependencies"],
                            cwd=npm_cache_dir,
                            stdout=df,
                            stderr=devnull,
                            bufsize=-1)
                    # dep_json = proc_read(proc, [0, 7])
                    # dep_dict = json.loads(dep_json)
                    process.wait()
        try:
            with open(dep_file, "r") as df:
                dep_dict = json.load(df)
                for sub_name in dep_dict.keys():
                    if sub_name not in known_depends and sub_name not in found:
                        found.append(sub_name)
        except ValueError:
            # This can happen in weird situations - the file is empty.
            # Replace the file with a valid but empty json file.
            with open(dep_file, "w") as df:
                df.write("{}")
    return known_depends


def replace_tokens(token_dict, src):
    assert isinstance(token_dict, dict)
    assert isinstance(src, str)

    with open(src, 'r') as f:
        ret = f.read()
        for k, v in token_dict.items():
            ret = ret.replace('@{0}@'.format(k), v)
        return ret


def create_token_dict(config):
    return {
        "db_prefix": config.db_prefix
    }
