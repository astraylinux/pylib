#!/usr/bin/python
#coding=utf-8
import os,sys
from tb import net

class Test:
	def __init__(self):
		pass

	def DownloadFile(self):
		down_url = "https://lh4.googleusercontent.com/-nnK8niqiGHk/AAAAAAAAAAI/AAAAAAAAAAA/Dys6DBHy5w4/s24-c/photo.jpg"
		local = "./data/downloadtest.jpg"
		if net.DownloadFile(down_url,local,timeout=20):
			if os.path.getsize(local) == 349:
				return True
		return False


if __name__ == "__main__":
	test = Test()
	print "1,Test DownloadFile:",
	print test.DownloadFile()
