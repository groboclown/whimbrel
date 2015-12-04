#!/usr/bin/python

import os
import sys

sys.path.append(sys.argv[0] == '' and os.path.curdir or os.path.dirname(sys.argv[0]))
from installer.whimbrel.install.cfg import read_config
from installer.whimbrel.install.util import out
from installer.whimbrel import install_db
from installer.whimbrel.install.lambdas import install_lambdas

config_file = len(sys.argv) > 1 and sys.argv[1] or "setup.config"
out.action("Setup", "Reading configuration from {0}".format(config_file))
if not os.path.exists(config_file):
    out.status("FAIL")
    exit()
config = read_config(config_file)
out.status("OK")

targets = ['db', 'lambdas']
if len(sys.argv) > 1:
    targets = sys.argv[1:]

for target in targets:
    if target == 'db':
        install_db(config)
    elif target == 'lambdas':
        install_lambdas(config)
