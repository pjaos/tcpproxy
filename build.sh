#!/bin/sh
rm -rf dist
rm -rf doc
doxygen
python3 -m build
