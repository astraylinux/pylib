#!/usr/bin/python
#coding=utf-8
"""
	Unit test for net.py.
"""
import os
import sys
from pylib import net

def download_file():
	"""
		download my picture for test download.
		function 'download_file' must check the file size.
	"""
	down_url = "https://avatars1.githubusercontent.com/u/4121264?v=3&s=460"
	print down_url
	exit()
	local = "./data/downloadtest.jpg"
	if net.download_file(down_url, local, timeout=20):
		if os.path.getsize(local) == 349:
			return True
	return False


if __name__ == "__main__":
	step = "all"
	if len(sys.argv) > 1:
		step = sys.argv[1]
	if step == "1" or step == "all":
		print "1,Test DownloadFile:",
		print download_file()
