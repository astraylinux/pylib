#!/usr/bin/python
#coding=utf-8
import urllib
import urllib2
import gzip
import time
import random
import StringIO
import os
import traceback

CODES = ["301", "302", "303", "304", "307", "400", "404", "401", "403", \
		"405", "406", "408", "500", "501", "502", "503", "504", "505"]
NO_RETRY = [301, 302, 303, 304, 307, 400, 401, 403, 404, 405, 406, 500, \
		501, 502, 503, 504, 505]

#some common net operation

def de_gzip(data):
	"""decomporess data from gzip
	"""
	cmps = StringIO.StringIO(data)
	gzipper = gzip.GzipFile(fileobj=cmps)
	return gzipper.read()

def post(url, data, heads=None, datatype=True):
	"""http post
		data: dictionary struct, key value of the post data
		heads: dictionaray struct, http head
		datatype: define the return data
			True: will return string
			False: return the http object response
	"""
	try:
		rep_header = {}
		request = urllib2.Request(url)
		data = urllib.urlencode(data)
		if heads:
			for key in heads:
				request.add_header(key, heads[key])
		response = urllib2.urlopen(request, data, timeout=10)
		code = response.getcode()
		rhead = response.info()
		rep_header["code"] = int(code)
		for key, val in	rhead.items():
			rep_header[key] = val
		if datatype:
			return (rep_header, response.read())
		return (rep_header, response)
	except EnvironmentError, msg:
		#print str(msg)
		if "404" in str(msg):
			return ({"code":404}, "")
		else:
			return ({"code":-1}, "")

def _get_error_code(e_str):
	for code in CODES:
		if code in e_str:
			return int(code)
	if "page not find" in e_str:
		return 404
	return -1

def get(url, heads=None, timeout=12):
	""" Http Get.
		Content-Length limit 10048576(10MB).
	"""
	fails = 0
	html = ""
	rep_header = {}
	rhead = {}
	code = 200
	while fails < 3:
		try:
			request = urllib2.Request(url)
			request.add_header("version", "HTTP/1.1")
			request.add_header("Accept-Encoding", "identity")
			if heads:
				for key in heads:
					request.add_header(key, heads[key])

			res_page = urllib2.urlopen(request, timeout=timeout)
			code = res_page.getcode()
			rhead = res_page.info()
			if ("Content-Length" in	rhead) and \
					int(rhead['Content-Length']) > 10048576:
				code = 99
				html = ""
			else:
				html = res_page.read()

			if "Content-Encoding" in rhead:
				if 'gzip' in rhead["Content-Encoding"]:
					html = de_gzip(html)
			break
		except EnvironmentError, msg:
			code = _get_error_code(str(msg))
			if code in NO_RETRY:
				rep_header["code"] = code
				return (rep_header, "")
			fails = fails + 1
			time.sleep(0.5)

	rep_header["code"] = code
	for key, val in	rhead.items():
		rep_header[key] = val
	return (rep_header, html)

#================================ 使用代理

G_PROXY_LIST = []
def init_proxy(proxy_file):
	"""
		Load proxy config file to initialize G_PROXY_LIST,
		proxy config format is => ip_addr:port\tdescription
		proxy_get and proxy_post will use the proxies in
		G_PROXY_LIST randomly.
	"""
	f_proxy = open(proxy_file, "r+")
	lines = f_proxy.readlines()
	f_proxy.close()
	count = 0
	for line in lines:
		if line[0] == "#":
			continue
		line = line.replace("\t", " ")
		line = line.replace("\n", "")
		ip_addr = line.split(" ")[0]
		desc = line.split(" ")[-1]
		proxy = {"http":ip_addr, "count":count, "desc":desc}
		count = count + 1
		G_PROXY_LIST.append(proxy)

def proxy_post(url, data, heads=None, datatype=True):
	"""
		Http get use proxy. Must had call init_proxy() before.
		datatype: define the return data
			True: will return string
			False: return the http object response
	"""
	retry = 3
	rep_header = {}
	rhead = {}
	proxy = G_PROXY_LIST[random.randint(0, len(G_PROXY_LIST)-1)]
	proxy_handler = urllib2.ProxyHandler(proxy)
	opener = urllib2.build_opener(proxy_handler)
	request = urllib2.Request(url)
	data = urllib.urlencode(data)
	code = 200
	if heads:
		for key in heads:
			request.add_header(key, heads[key])
	while retry:
		try:
			response = opener.open(request, data, timeout=10)
			code = response.getcode()
			rhead = response.info()
			if datatype:
				return ({"code":code}, response.read())
			else:
				return ({"code":code}, response)
		except EnvironmentError, msg:
			retry = retry - 1
			time.sleep(1)
			code = _get_error_code(str(msg))
			if code in NO_RETRY:
				rep_header["code"] = code
				return (rep_header, "")

	rep_header["code"] = code
	for key, val in	rhead.items():
		rep_header[key] = val
	return (rep_header, "")

def proxy_get(url, heads=None, datatype=True):
	"""
		Http get use proxy. Must had call init_proxy() before.
		datatype: define the return data
			True: will return string
			False: return the http object response
	"""
	retry = 3
	rep_header = {}
	rhead = {}
	proxy = G_PROXY_LIST[random.randint(0, len(G_PROXY_LIST)-1)]
	proxy_handler = urllib2.ProxyHandler(proxy)
	opener = urllib2.build_opener(proxy_handler)
	request = urllib2.Request(url)
	if heads:
		for key in heads:
			request.add_header(key, heads[key])
	while retry:
		try:
			response = opener.open(request, timeout=10)
			code = response.getcode()
			rhead = response.info()
			dict_head = {}
			for key, value in rhead.items():
				dict_head[key] = value
			rhead = dict_head
			rhead["code"] = int(code)

			if datatype:
				html = response.read()
				if "Content-Encoding" in rhead and 'gzip' in rhead["Content-Encoding"]:
					html = de_gzip(html)
				return (rhead, html)
			else:
				return (rhead, response)
		except EnvironmentError, msg:
			retry = retry - 1
			if "304" in str(msg):
				rep_header["code"] = 304
				return (rep_header, "")
			time.sleep(1)
			if retry == 0:
				print proxy
				print traceback.format_exc(str(msg))
				if "404" in str(msg):
					return ({"code":404}, "")
				else:
					return ({"code":-1}, "")

	rep_header["code"] = code
	for key, val in	rhead.items():
		rep_header[key] = val
	return (rep_header, "")

def download_file(url, local, head=None, timeout=10):
	"""Download file to local."""
	retry = True
	while retry:
		try:
			request = urllib2.Request(url)
			if head:
				for key, value in head.items():
					request.add_header(key, value)
			request = urllib2.urlopen(request, timeout=timeout)
			length = 0
			headinfo = request.info()
			if "Content-Length" in headinfo:
				length = int(headinfo["Content-Length"])
			tmpdata = request.read(64*1024)
			file_handle = open(local, "wb")
			while tmpdata:
				file_handle.write(tmpdata)
				tmpdata = request.read(64*1024)
			file_handle.close()
			request.close()
			if length > 0:
				if os.path.getsize(local) == length:
					return True
			os.remove(local)
			return False
		except EnvironmentError, msg:
			print msg
			retry = False
		return False
