#!/bin/bash
cd "$(dirname "$0")"
/usr/local/bin/python3 -m pip install -r requirements.txt --user
/usr/local/bin/python3 platformer.py 