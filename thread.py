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
		self._num = num
		self._func = func
		self._queue = queue
		self._alive = False

	def run(self):
		self._alive = True
		while True:
			try:
				item = self._queue.get_nowait()
			except:
				break
			self._func(item, self._num, self._queue.qsize())
		self._alive = False

def run(datas, func, num, space=1, block=True, check_space=1):
	"""
		Start 'num' thread to use func deal the datas.
		datas must be a list with unit data that need deal.
		Space is the interval of two thread start.
	"""
	queue = Queue.Queue()
	threads = []
	for data in datas:
		queue.put(data)
	for index in range(0, num):
		thread = Thread(index, func, queue)
		thread.start()
		threads.append(thread)
		time.sleep(space)
	if block:
		thread_count = len(threads)
		while True:
			time.sleep(check_space)
			stop_count = 0
			for thread in threads:
				if not thread._alive:
					stop_count += 1
			if stop_count == thread_count:
				break
