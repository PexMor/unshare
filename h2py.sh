#!/bin/bash

#
# This script runs a C header to python conversion to avoid typos
#
# h2py can be also downoladed from (copied here for convenience as well)
# https://github.com/python/cpython/blob/master/Tools/scripts/h2py.py
# https://hg.python.org/cpython/file/70274d53c1dd/Tools/scripts/h2py.py
#
python h2py.py /usr/include/linux/sched.h
python h2py.py /usr/include/linux/fs.h
