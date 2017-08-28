#!/bin/bash
export PYTHONPATH=$PWD/python-modules:$PYTHONPATH
python3 -m unittest discover
