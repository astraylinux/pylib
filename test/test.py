#!/usr/bin/python
#coding=utf-8
"""
	Unit test for util.py.
"""
import os
import sys
from pylib import util

lines = util.get_lines("/var/log/syslog")
for line in lines:
	print line

