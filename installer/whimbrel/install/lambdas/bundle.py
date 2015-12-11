"""
Create the install bundles for the lambdas.
"""

import os
import zipfile
import subprocess
import shutil
from ..cfg import Config


def bundle_lambdas(config, lambda_dict):
    """
    Creates the bundle zip files from the lambdas defined in the
    module `get_lambdas()` call.

    :param config:
    :param lambda_dict:
    :return:
    """
    assert isinstance(config, Config)

    overrides_dir = config.override_lambda_dir

    ret = {}
    for lambda_name, lambda_def in lambda_dict.items():
        # TODO: both copy files and create zip,
        # if a "compile" flag is set in the config.
        # Allow for user-overwriting files on a one-by-one
        # basis.

        lambda_basedir = os.path.join(config.basedir, ".lambdas.d", lambda_name)

        product = "product" in lambda_def and lambda_def["product"] or None
        for cat, cat_def in lambda_def.items():
            if cat == "product":
                zip_filename = os.path.join(lambda_basedir, lambda_name + ".zip")
                ret[lambda_name] = {
                    # TODO version, etc
                    "name": lambda_name,
                    "zip": zip_filename
                }
            else:
                zip_filename = os.path.join(lambda_basedir,
                    "{0}-{1}.zip".format(lambda_name, cat))
            cat_def = _join_defs(product, cat_def)
            _install_lambda(config, lambda_name, cat_def,
                os.path.join(lambda_basedir, cat), zip_filename)

    return ret


def _install_lambda(config, lambda_name, lambda_def, lambda_outdir, lambda_zip_filename):
    if os.path.exists(lambda_outdir):
        shutil.rmtree(lambda_outdir)
    if os.path.exists(lambda_zip_filename):
        os.unlink(lambda_zip_file)
    if not os.path.isdir(os.path.dirname(lambda_zip_filename)):
        os.makedirs(os.path.dirname(lambda_zip_filename))
    lambda_zip = zipfile.ZipFile(lambda_zip_filename, "w", compression=zipfile.ZIP_DEFLATED)
    try:
        if "npm" in lambda_def:
            # HUGE TODO
            # This currently doesn't pick up any inner dependencies that
            # the pulled-in node module relies upon.
            npm_cache_dir = _get_npm_cache_dir(config)
            for npm_name in lambda_def['npm']:
                npm_install(config, npm_name)
                module_dir = os.path.join("node_modules", npm_name)
                _copy_bundle_dir(
                    os.path.join(npm_cache_dir, module_dir),
                    module_dir, lambda_outdir, lambda_zip)
        if "copy-dirs" in lambda_def:
            for copy_dir_def in lambda_def['copy-dirs']:
                src_dir = os.path.join(config.basedir, *copy_dir_def["srcdir"])
                dest_dir = os.path.join(*copy_dir_def["destdir"])
                _copy_bundle_dir(src_dir, dest_dir, lambda_outdir, lambda_zip)
        if "copy-files" in lambda_def:
            for copy_file_def in lambda_def['copy-files']:
                src = os.path.join(config.basedir, *copy_file_def["src"])
                dest = os.path.join(*copy_file_def["dest"])
                _copy_bundle_file(src, dest, lambda_outdir, lambda_zip)
        # tokenized
        # user-overrides

    finally:
        lambda_zip.close()


def _get_npm_cache_dir(config):
    return os.path.join(config.basedir, ".npm_cache.d")


def npm_install(config, name):
    assert isinstance(config, Config)
    npm_cache_dir = _get_npm_cache_dir(config)
    module_install_dir = os.path.join(npm_cache_dir, "node_modules", name)
    if os.path.isdir(module_install_dir):
        return module_install_dir
    if not os.path.isdir(npm_cache_dir):
        os.makedirs(npm_cache_dir)
    subprocess.check_call([config.npm_exec, "install", name], cwd=npm_cache_dir)
    if os.path.isdir(module_install_dir):
        return module_install_dir
    raise Exception("npm install did not create " + module_install_dir)


def _replace_tokens(token_dict, src):
    assert isinstance(token_dict, dict)
    assert isinstance(src, str)

    with open(src, 'r') as f:
        ret = f.read()
        for k, v in token_dict.items():
            ret = ret.replace('@{0}@'.format(k), v)
        return ret


def _create_token_dict(config):
    assert isinstance(config, Config)

    return {
        "db_prefix": config.db_prefix
    }


def _join_defs(*defs):
    ret = {
        "exec": [],
        "copy-files": [],
        "copy-dirs": [],
        "npm": [],
        "tokenized": []
    }
    for src in defs:
        if src is not None:
            for key in ret.keys():
                if key in src and src[key] is not None:
                    ret[key].extend(src[key])
    return ret


def _copy_bundle_dir(src_dir, archive_path, out_dir, zip_file):
    copy_dirs = [[src_dir, archive_path]]
    while len(copy_dirs) > 0:
        next_src_dir, next_archive_path = copy_dirs.pop()
        for name in os.listdir(next_src_dir):
            src_filename = os.path.join(next_src_dir, name)
            dest_filename = os.path.join(next_archive_path, name)
            if os.path.isdir(src_filename):
                copy_dirs.append([src_filename, dest_filename])
            else:
                _copy_bundle_file(src_filename, dest_filename, out_dir, zip_file, None)


def _copy_bundle_file(src_file, archive_file, out_dir, zip_file, token_dict):
    out_file = os.path.join(out_dir, archive_file)
    if not os.path.isdir(os.path.dirname(out_file)):
        os.makedirs(os.path.dirname(out_file))
    if token_dict is not None:
        text = _replace_tokens(token_dict, src_file)
        zip_file.writestr(archive_file, text)
        with open(out_file, "wb") as f:
            f.write(text)
    else:
        shutil.copyfile(src_file, out_file)
        zip_file.write(src_file, arcname=archive_file)
