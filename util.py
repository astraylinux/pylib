#!/usr/bin/python
#coding=utf-8
import os
import sys
import redis
import logging
import time
import socket
import hashlib
import datetime
import random
import re
from decimal import Decimal
reload(sys)
sys.setdefaultencoding("utf-8")

PINYIN_LIB = {}
LANGCONV = {}
#============================================================= simple function
def get_redis_clinet(server):
	""" Connect redis use config: {"host":"127.0.0.1", "port":6379, "db":1}"""
	return redis.Redis(host=server["host"], port=server["port"], db=server["db"])

def log_config(logfile, level=logging.INFO, fmt=None):
	""" Quick to setting logging """
	if not fmt:
		fmt = "[%(asctime)s][%(filename)s][%(lineno)d][%(levelname)s]::%(message)s"
	logging.basicConfig(filename=logfile, level=level, format=fmt)

def get_now_datetime():
	""" Quick to get normal date time """
	return time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time()))

def get_date(offset=-1):
	"""
		Get date with offset.
		offset < 0, it's the pass offset data.
	 	offset > 0, it's the future.
	"""
	today = datetime.date.today()
	offset_d = datetime.timedelta(days=offset)
	the_date = today + offset_d
	return str(the_date)

def get_micro_time():
	""" Get decimal time to micro second."""
	return Decimal(time.time())

def date2second(the_date):
	""" Trans the datetime to second from 1970"""
	return int(time.mktime(time.strptime(str(the_date)[:19], "%Y-%m-%d %H:%M:%S")))

def second2date(second):
	""" Trans the time.time() second to datetime """
	time_array = time.localtime(second)
	return time.strftime("%Y-%m-%d %H:%M:%S", time_array)

def get_ip():
	""" Get you ip """
	return socket.gethostbyname(socket.gethostname())

def md5(string):
	return hashlib.md5(string).hexdigest()

#============================================================= language
def trans2py(cn_str, entire=True):
	"""
		Trans the Chinese word to pinyin.
		if entire=False, will only get the first char each word.
	"""
	if not PINYIN_LIB:
		#init PINYIN_LIB from the word lib
		path = os.path.dirname(__file__)
		fpoint = open(path + "/data/pinyin-utf8.db", "r+")
		lines = fpoint.readlines()
		fpoint.close()
		for line in lines:
			row = line.replace("\n", "").split(",")
			PINYIN_LIB[row[0]] = row[1][:-1]

	i = 0
	rstr = ""
	cn_str = cn_str.encode("utf-8")
	try:
		cn_str = cn_str.encode("utf-8")
	except UnicodeDecodeError:
		return ""

	cn_str = unicode(cn_str)
	all_cn = ""
	row = cn_str.split(" ")
	for word in row:
		if all_cn != "":
			all_cn += " "
		matches = re.findall(u"[\u4e00-\u9fa5]", word)
		for match in matches:
			all_cn += str(match)

	if not all_cn:
		return ""
	while i < len(all_cn):
		one = all_cn[i:i+3]
		if one in PINYIN_LIB:
			if not entire:
				rstr += PINYIN_LIB[one][0]
			else:
				rstr += PINYIN_LIB[one]
		if i+3 < len(all_cn) and all_cn[i+3] == " ":
			rstr += " "
			i += 1
		i = i+3
	return rstr

def convert_sp2td(cn_str):
	""" Conver simple Chinese to traditional Chinese """
	if not LANGCONV:
		from pylib import _langconv
		LANGCONV["lib"] = _langconv
	cn_str = LANGCONV["lib"].Converter('zh-hant').convert(cn_str.decode('utf-8'))
	return cn_str.encode('utf-8')

def convert_td2sp(cn_str):
	""" Conver traditional Chinese to simple Chinese """
	if not LANGCONV:
		from pylib import _langconv
		LANGCONV["lib"] = _langconv
	cn_str = LANGCONV["lib"].Converter('zh-hans').convert(cn_str.decode('utf-8'))
	return cn_str.encode('utf-8')

#====================================================== struct
def get_random_list(olist, num=None):
	""" Get a random list from alist, weighted with propertys """
	#从现有队列生成随机队列, 可以加权
	newlist = list(olist)
	if num == None:
		num = len(newlist)

	random.shuffle(newlist)
	return newlist[0:num]

#======================================================== Algorithm
def sort_list(key_map, desc=False):
	""" Sort a list """
	backitems = list(key_map)
	backitems.sort()
	if desc:
		return backitems[::-1]
	else:
		return backitems

def dict_sort_list(dict_or_list, key, desc=False):
	""" Return a list, that sort the dict by the key, not change the dict """
	if isinstance(dict_or_list, dict):
		backitems = [[v[1][key], v[0]] for v in dict_or_list.items()]
	elif isinstance(dict_or_list, list):
		backitems = [[v[key], v] for v in dict_or_list]
	else:
		return []
	backitems.sort()
	if desc:
		return [backitems[i][1] for i in range(len(backitems)-1, -1, -1)]
	else:
		return [backitems[i][1] for i in range(0, len(backitems))]

def list2str(items, sep):
	""" Change list to string, sep is the separate. """
	rstr = ""
	for item in items:
		rstr = rstr + str(item) + sep
	return rstr[:-1]

def dict_sort(adict, key, desc=False, num=None):
	""" Sort dict by key, return a new dict, num limit number."""
	rlist = dict_sort_list(adict, key, desc)
	n_map = {}
	for key in rlist[:num]:
		n_map[key] = adict[key]
	return n_map

def list2dict(keys, rows):
	""" Change list to dict with specifi key. Index map index."""
	return dict(zip(keys, rows))

#====================================================== File
def get_lines(file_name):
	""" Read all lines to a list from file."""
	fpoint = open(file_name, 'r')
	lines = fpoint.readlines()
	fpoint.close()
	for i in range(0, len(lines)):
		lines[i] = lines[i].replace('\n', '')
	return lines

def file_md5(file_name):
	""" Get file's md5."""
	file_in = None
	ret_md5 = ""
	try:
		file_in = open(file_name, "rb")
		md5 = hashlib.md5()
		str_read = ""
		while True:
			str_read = file_in.read(8096)
			if not str_read:
				break
			md5.update(str_read)
		ret_md5 = md5.hexdigest()
	except IOError:
		ret_md5 = ""
	finally:
		if file_in:
			file_in.close()
	return ret_md5

def del_duplicate(data_list, key=None):
	"""
		Remove duplicate item from list or dict.
		For list key=None, For dict, must appoint the key.
		The duplicate item position after will be delete.
	"""
	result = []
	tmp = {}
	for item in data_list:
		data = item
		if isinstance(item, dict):
			data = item[key]
		if not data in tmp:
			result.append(item)
			tmp[data] = 1
	return result

#============================================================== conversion
def bin2dec(string_num):
	""" Binary convert to decimal."""
	return str(int(string_num, 2))

def hex2dec(string_num):
	""" Hexadecimal convert to decimal."""
	return str(int(string_num.upper(), 16))

def dec2bin(string_num):
	""" Decimal convert to binary."""
	base = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'A', 'B', 'C', 'D', 'E', 'F']

	num = int(string_num)
	mid = []
	while True:
		if num == 0:
			break
		num, rem = divmod(num, 2)
		mid.append(base[rem])
	return ''.join([str(x) for x in mid[::-1]])

def dec2hex(string_num):
	""" Decimal convert to Hexadecimal."""
	base = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'A', 'B', 'C', 'D', 'E', 'F']
	num = int(string_num)
	mid = []
	while True:
		if num == 0:
			break
		(num, rem) = divmod(num, 16)
		mid.append(base[rem])
	return ''.join([str(x) for x in mid[::-1]])

def hex2bin(string_num):
	""" Hexadecimal convert to binary."""
	return dec2bin(hex2dec(string_num.upper()))

def bin2hex(string_num):
	""" Binary convert to hexadecimal."""
	return dec2hex(bin2dec(string_num))
