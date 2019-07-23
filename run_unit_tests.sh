#!/bin/bash
export PYTHONPATH=$PWD:$PYTHONPATH
python3 -m unittest discover test/
