#!/usr/bin/env python
# encoding: utf-8

import time
from pylib import thread


data = [1, 2, 3, 4, 5, 6, 7, 8]

def func(item, num, size):
	time.sleep(0.5)
	print item, num, size

thread.run(data, func, 3, space=0.1, check_space=0.5)
