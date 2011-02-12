#!/bin/bash
# a hook by default seems to run in the root of the repository root directory
hg update
projdir= `pwd`
../start.py projdir

