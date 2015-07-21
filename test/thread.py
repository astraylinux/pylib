#!/usr/bin/env python
# encoding: utf-8

import time
from pylib import thread


data = [1, 2, 3, 4, 5, 6, 7, 8]
res = ['a', 'b', 'c', 'd', 'e', 'f', 'g']

def func(item, res, num, size):
	time.sleep(0.5)
	print item, num, size, res

thread.run(data, func, 3, space=0.1, check_space=0.5, args=res)

print "end 1"

thread.run(data, func, 3, space=0.1, check_space=0.5, block=False)

print "end 2"

threads = thread.run(data, func, 3, space=0.1, check_space=0.5, block=False)

while thread.alive(threads):
	time.sleep(0.5)
	print "alive:", thread.alive(threads)

print "end 3"
