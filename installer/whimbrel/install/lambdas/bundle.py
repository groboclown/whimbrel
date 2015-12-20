"""
Create the install bundles for the lambdas.
"""

import os
import shutil
import json
from ..cfg import Config
from ..util import copy
from . import nodejs

# 1. For each module, copy/install the "library/node.js" child directories
#    into the npm cache dir.  Remove it in the npm cache directory first if it
#    already exists.
# 2. After the libraries are setup, then for each module:
#   1. For each child directory under "lambdas" that has a "package.json" file,
#      create the deployable bundle.  Optionally ignore the "test" subdirectory
#      when creating the zip.
#   2. The deployable bundle will include the node_modules subdirectory, which
#      will pull from the package.json file.  Note that this can include
#      the locally cached libraries.
#      The copy should include also using the "templates" section of the json
#      file to create templatized files, overwriting whatever may come in
#      from the source directory.
#   4. Run the unit tests (in the package.json scripts/test section).


def get_lambda_basedir(config):
    assert isinstance(config, Config)
    return os.path.join(config.basedir, ".lambdas.d")


def get_node_test_basedir(config):
    return get_lambda_basedir(config) + ".tests"


def bundle_modules(config, prepare_only=False):
    bundle_library_node_modules(config)
    ret = bundle_lambdas(config, prepare_only)
    bundle_tests(config)
    return ret


def bundle_library_node_modules(config):
    """
    Install all the node.js module libraries from the registered whimbrel modules.
    This MUST be done before the lambdas are installed.

    :param config:
    :return:
    """
    assert isinstance(config, Config)
    for module_name, module_dir in config.module_paths.items():
        base_node_module_dir = os.path.join(module_dir, 'library', 'node.js')
        if os.path.exists(base_node_module_dir):
            for fname in os.listdir(base_node_module_dir):
                d = os.path.join(base_node_module_dir, fname)
                if has_package_file(d):
                    _install_node_module_for(config, d, fname)


def bundle_lambdas(config, prepare_only=False):
    """

    :param prepare_only:
    :param config:
    :return:
    """
    assert isinstance(config, Config)
    ret = {}
    for module_name, module_dir in config.module_paths.items():
        lambda_base_dir = os.path.join(module_dir, 'lambdas')
        if os.path.isdir(lambda_base_dir):
            for name in os.listdir(lambda_base_dir):
                lambda_dir = os.path.join(lambda_base_dir, name)
                if has_package_file(lambda_dir):
                    _install_node_module_for(config, lambda_dir, name)
                    if not prepare_only:
                        lambda_out_dir = os.path.join(get_lambda_basedir(config), name)
                        _copy_node_module_into_with_templates(config, lambda_out_dir, name)
                        lambda_zip_file = os.path.join(get_lambda_basedir(config), name + ".zip")
                        copy.zip_dir(lambda_zip_file, lambda_out_dir)
                        ret[name] = lambda_zip_file
    return ret


def bundle_tests(config):
    """
    Installs the node libraries and lambdas into the test_dir, including
    all the dev dependencies and dependencies.

    :param config:
    :param test_dir:
    :return:
    """
    assert isinstance(config, Config)
    base_test_dir = get_node_test_basedir(config)
    ret = []
    for module_name, module_dir in config.module_paths.items():
        module_test_dir = os.path.join(base_test_dir, module_name)
        base_node_module_dir = os.path.join(module_dir, 'library', 'node.js')
        if os.path.exists(base_node_module_dir):
            for fname in os.listdir(base_node_module_dir):
                d = os.path.join(base_node_module_dir, fname)
                if has_package_file(d):
                    ret.append(_install_node_module_for(config, d, fname, module_test_dir, True))

        lambda_base_dir = os.path.join(module_dir, 'lambdas')
        if os.path.isdir(lambda_base_dir):
            for name in os.listdir(lambda_base_dir):
                lambda_dir = os.path.join(lambda_base_dir, name)
                if has_package_file(lambda_dir):
                    installed_dir = _install_node_module_for(config, lambda_dir, name, module_test_dir, True)
                    _copy_templates(config, installed_dir)
                    ret.append(installed_dir)

    return ret


def _install_node_module_for(config, library_dir, library_name, dest_root_dir=None, include_tests=False):
    """
    Installs the node module into the node module cache directory, which
    includes downloading all dependencies.  The dev dependencies are
    loaded into the cache, but are not included in the internal
    node_modules dir.

    :param config:
    :param library_dir:
    :param library_name:
    :param dest_root_dir: root directory where the module will be installed into,
        with the library_name as the subdirectory.
    :param include_tests: should the test directory and dependencies be installed?
    :return: installed-into directory
    """
    assert isinstance(config, Config)
    package = load_package_file(library_dir)
    if dest_root_dir is None:
        dest_root_dir = nodejs.get_npm_cache_dir(config)
    dest_dir = os.path.join(dest_root_dir, library_name)
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir, ignore_errors=True)
    if not os.path.exists(os.path.dirname(dest_dir)):
        os.makedirs(os.path.dirname(dest_dir))
    shutil.copytree(library_dir, dest_dir)
    if not include_tests:
        test_dir = os.path.join(dest_dir, 'test')
        if os.path.isdir(test_dir):
            shutil.rmtree(test_dir)

    if 'dependencies' in package:
        # TODO use a real tool to install these
        for dep_name in package['dependencies'].keys():
            _copy_node_module_into(config, dest_dir, dep_name)
    # Dev dependencies are only installed into the test directory when the tests are run.
    # However, we'll cache the node module here, so that the test run can go much faster.
    if 'devDependencies' in package:
        for dep_name in package['devDependencies'].keys():
            if include_tests:
                _copy_node_module_into(config, dest_dir, dep_name)
            else:
                nodejs.npm_install(config, dep_name)

    # Setting up the templates should only done when the lambda is actually bundled.

    return dest_dir


def _copy_node_module_into_with_templates(config, dest_dir, module_name):
    installed_dirs = _copy_node_module_into(config, dest_dir, module_name)
    for installed_dir in installed_dirs:
        _copy_templates(config, installed_dir)


def _copy_templates(config, installed_dir):
    package = load_package_file(installed_dir)
    if package is not None:
        if 'templates' in package:
            tokens = _create_token_dict(config)
            for src_name, dest_name in package['templates'].items():
                src_path = os.path.join(installed_dir, src_name)
                dest_path = os.path.join(installed_dir, dest_name)
                if not os.path.isdir(os.path.dirname(dest_path)):
                    os.makedirs(os.path.dirname(dest_path))
                with open(dest_path, "w") as f:
                    f.write(copy.replace_tokens(tokens, src_path))


def _copy_node_module_into(config, dest_dir, module_name):
    src_dirs = nodejs.npm_install(config, module_name)
    dest_dirs = []
    for src_dir in src_dirs:
        dep_name = os.path.basename(src_dir)
        sub_dir = os.path.join(dest_dir, 'node_modules', dep_name)
        if not os.path.exists(os.path.dirname(sub_dir)):
            os.makedirs(os.path.dirname(sub_dir))
        shutil.copytree(src_dir, sub_dir, symlinks=False)
        dest_dirs.append(sub_dir)
    return dest_dirs


def has_package_file(node_module_dir):
    return os.path.isfile(os.path.join(node_module_dir, 'package.json'))


def load_package_file(node_module_dir):
    package_file = os.path.join(node_module_dir, 'package.json')
    package = None
    if os.path.isfile(package_file):
        with open(package_file, "r") as f:
            package = json.load(f)
    return package


def _create_token_dict(config):
    assert isinstance(config, Config)

    return {
        "db_prefix": config.db_prefix
    }
