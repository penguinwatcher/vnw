#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import logging

def exec_cmd(cmd):
    logging.debug("Executing ... %s" % cmd)
    returncode = 0
    returncode = subprocess.call(cmd.strip().split(" "))
    return returncode



