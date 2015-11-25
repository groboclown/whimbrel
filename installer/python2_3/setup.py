#!/usr/bin/python

import sys
import os
sys.path.append(sys.argv[0] == '' and os.path.curdir or os.path.dirname(sys.argv[0]))
from whimbrel.install.cfg import read_config
from whimbrel.install.util import out
from whimbrel.install.db import install_db

config_file = len(sys.argv) > 1 and sys.argv[1] or "setup.config"
out.action("Setup", "Reading configuration from {0}".format(config_file))
if not os.path.exists(config_file):
    out.status("FAIL")
    exit()
config = read_config(config_file)
out.status("OK")

install_db(config)
