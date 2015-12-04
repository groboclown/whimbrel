"""
Create the install bundles for the lambdas.
"""

import os
import zipfile
from ..cfg import Config


def create_modules(config, template_dir):
    """
    Returns a dictionary of (module name) -> file contents.

    :param template_dir:
    :return:
    """
    token_dict = _create_token_dict(config)
    ret = {}
    for name in os.listdir(template_dir):
        filename = os.path.join(template_dir, name)
        (module_name, ext) = os.path.extsep(name)[1]
        if os.path.isfile(filename) and ext == '.js':
            ret[module_name] = _replace_tokens(token_dict, filename)
    return ret


def bundle_js(config, js_file, output_zip_file_name, modules):
    assert isinstance(config, Config)
    assert isinstance(str, js_file)
    assert os.path.isfile(js_file)

    out_zip = zipfile.ZipFile(output_zip_file_name, "w", compression=zipfile.ZIP_DEFLATED)
    out_zip.writestr(os.path.basename(js_file), js_file)
    for module_name, text in modules.items():
        out_zip.writestr("node_modules/{0}/index.js".format(os.path.basename(js_file)), text)
    out_zip.close()


def _replace_tokens(token_dict, src):
    assert isinstance(token_dict, dict)
    assert isinstance(src, str)

    with open(src, 'r') as f:
        ret = f.read()
        for k, v in token_dict.items():
            ret = ret.replace('@{0}@'.format(k), y)
        return ret


def _create_token_dict(config):
    assert isinstance(config, Config)

    return {
        "db_prefix": config.db_prefix
    }
