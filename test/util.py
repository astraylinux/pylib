#!/usr/bin/python
#coding=utf-8
"""
	Unit test for util.py.
"""
import os
import sys
from pylib import util

def trans2py():
	""" Test trans2py."""
	words = {"中国":"zhongguo", "下雨":"xiayu",\
			"电脑":"diannao"}
	for (cn_word, py_word) in words.items():
		trans_str = util.trans2py(cn_word)
		if not py_word == trans_str:
			print cn_word, py_word, trans_str

if __name__ == "__main__":
	step = "all"
	if len(sys.argv) > 1:
		step = sys.argv[1]
	if step == "trans2py" or step == "all":
		print "==== trans2py"
		trans2py()
