#!/bin/bash

cd "$( dirname "${BASH_SOURCE[0]}" )"

python fetch.py
python water.py
python cities.py
