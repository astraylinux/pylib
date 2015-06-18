#!/usr/bin/python
#coding=utf-8
"""
	Unit test for net.py.
"""
import os
import sys
from pylib import expath, net

def xpath():
	print "Test expath.xpath"
	doc_url = "http://zhidao.baidu.com/question/92222933.html"

	pick_config = {\
		"title": {"key": """/html/head/title/text()"""},
		"keywords": {"key": """/html/head/meta[@name="keywords"]/@content"""},
		"description": {"key":\
				"""/html/head/meta[@name="description"]/@content"""},\
	}

	(headers, html) = net.get(doc_url)
	if not headers["code"] == 200:
		print "net.get failed!"
	picker = expath.XPath(doc_url, html, code="gbk")
	ret_dict = picker.pick(pick_config)
	for key, value in ret_dict.items():
		print key, "==>", value
	print

def json():
	print "Test expath.json"
	doc_url = "http://itunes.apple.com/cn/lookup?id=444934666"

	pick_config = {\
		"appleid": {"key": """/results/0/trackId"""},
		"name": {"key": """/results/0/trackName"""},
		"version": {"key": """/results/0/version"""},\
	}

	(headers, html) = net.get(doc_url)
	if not headers["code"] == 200:
		print "net.get failed!"
	picker = expath.XJson(doc_url, html, code="utf8")
	ret_dict = picker.pick(pick_config)
	for key, value in ret_dict.items():
		print key, "==>", value
	print

if __name__ == "__main__":
	step = "all"
	if len(sys.argv) > 1:
		step = sys.argv[1]
	if step == "xpath" or step == "all":
		xpath()
	if step == "json" or step == "all":
		json()

