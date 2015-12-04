"""
Create the install bundles for the lambdas.
"""

import os
import zipfile
from ..cfg import Config

# TODO look at creating a resource that stores the configuration data, rather than
# building it into a template file.  Need to investigate lambdas and how they load their resources.
# Looks like the `dotenv` js resource can help here.


def bundle_js(config, js_file, output_zip_file_name):
    assert isinstance(config, Config)
    assert isinstance(str, js_file)
    assert os.path.isfile(js_file)

    out_zip = zipfile.ZipFile(output_zip_file_name, "w", compression=zipfile.ZIP_DEFLATED)
    out_zip.writestr(os.path.basename(js_file), replace_tokens(config, js_file))
    out_zip.close()


def replace_tokens(config, src):
    assert isinstance(config, Config)
    assert isinstance(str, src)
