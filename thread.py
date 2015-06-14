#!/usr/local/bin/python
#coding=utf-8
import threading
import time
import Queue

class Thread(threading.Thread):
	"""
		A simple thread class, input a data queue, and a callback
		function, will use the function deal each data in each thread.
		Use the run() function to quick start.
	"""
	def __init__(self, num, func, queue):
		threading.Thread.__init__(self)
		self.num = num
		self.func = func
		self.queue = queue

	def run(self):
		while True:
			item = self.queue.get()
			if item is False:
				time.sleep(1)
				return
			else:
				self.func(item, self.num, self.queue.qsize())
			if self.queue.qsize() == 0:
				time.sleep(1)
				return

def run(datas, func, num, space=1):
	"""
		Start 'num' thread to use func deal the datas.
		datas must be a list with unit data that need deal.
		Space is the interval of two thread start.
	"""
	queue = Queue.Queue()
	for data in datas:
		queue.put(data)
	for index in range(0, num):
		thread = Thread(index, func, queue)
		thread.start()
		time.sleep(space)
