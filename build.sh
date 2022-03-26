#!/bin/sh
rm -rf dist
rm -rf doc
doxygen
python3 -m build
# This builds a deb file. If a deb installer is required.
sudo pipenv2deb