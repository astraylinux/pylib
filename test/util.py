#!/usr/bin/python
#coding=utf-8
"""
	Unit test for util.py.
"""
import os
import sys
import commands
from pylib import util

def trans2py():
	""" Test trans2py."""
	words = {"中国":"zhongguo", "下雨":"xiayu",\
			"电脑":"diannao"}
	for (cn_word, py_word) in words.items():
		trans_str = util.trans2py(cn_word)
		if not py_word == trans_str:
			print cn_word, py_word, trans_str

def convert_sp_and_td():
	""" Simple Chinese and traditional Chinese convert."""
	words = {"中国":"中國", "视频":"視頻", "电脑":"電腦"}
	for (sp_word, td_word) in words.items():
		convert_td = util.convert_sp2td(sp_word)
		convert_sp = util.convert_td2sp(td_word)
		if not convert_sp == sp_word:
			print "td => sp: %s %s"%(td_word, convert_sp)
		if not convert_td == td_word:
			print "sp => td: %s %s"%(sp_word, convert_td)

def algorithm():
	""" test get_random_list sort_list, dict_sort_list."""
	print "==== get_random_list"
	origin_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
	random_list = util.get_random_list(origin_list, 10)
	if origin_list[:10] == random_list:
		print random_list

	print "==== sort_list"
	origin_list = [3, 5, 1, 4, 7, 2, 0, 6]
	aesc_list = [0, 1, 2, 3, 4, 5, 6, 7]
	desc_list = [7, 6, 5, 4, 3, 2, 1, 0]
	sort_list = util.sort_list(origin_list)
	if sort_list != aesc_list:
		print "aesc", sort_list
	sort_list = util.sort_list(origin_list, desc=True)
	if sort_list != desc_list:
		print "desc", sort_list

	print "==== dict_sort_list"
	origin_dict = {"a":{"s":1}, "b":{"s":3}, "c":{"s":0}}
	origin_list = [{"s":1}, {"s":3}, {"s":0}]
	sort_list = util.dict_sort_list(origin_dict, "s")
	sort_dict_list = util.dict_sort_list(origin_list, "s")
	sort_dict = util.dict_sort(origin_dict, "s")
	if sort_list != ['c', 'a', 'b']:
		print "list", sort_list
	if sort_dict_list != [{'s': 0}, {'s': 1}, {'s': 3}]:
		print "dict_list", sort_dict_list
	if sort_dict != {'a': {'s': 1}, 'c': {'s': 0}, 'b': {'s': 3}}:
		print "dict", sort_dict

	print "==== list to dict"
	list_k = [1, 2, 3]
	list_v = ["a", "b", "c"]
	rdict = util.list2dict(list_k, list_v)
	if rdict != {1: 'a', 2: 'b', 3: 'c'}:
		print rdict

def md5_test():
	print "==== md5"
	test_file = "/var/log/syslog"
	fmd5 = util.file_md5(test_file)
	cmd = "echo -n `md5sum /var/log/syslog|awk '{print $1}'`"
	cmd_ret = commands.getstatusoutput(cmd)
	if fmd5 != cmd_ret[1]:
		print "file_md5:", fmd5, cmd_ret[1]
	md5 = util.md5("12345")
	if md5 != "827ccb0eea8a706c4c34a16891f84e7b":
		print "md5:", md5, "827ccb0eea8a706c4c34a16891f84e7b"

def del_duplicate():
	print "==== del_duplicate"
	origin_list = [{"a":1, "b":2}, {"a":3, "b":4}, {"a":1, "b":3}]
	retlist = util.del_duplicate(origin_list, "a")
	if retlist != [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]:
		print "dict_list", retlist
	origin_list = [2, 3, 2]
	retlist = util.del_duplicate(origin_list)
	if retlist != [2, 3]:
		print "list", retlist

if __name__ == "__main__":
	step = "all"
	if len(sys.argv) > 1:
		step = sys.argv[1]
	if step == "trans2py" or step == "all":
		print "==== trans2py"
		trans2py()
	if step == "sptd" or step == "all":
		print "==== convert_sp_td"
		convert_sp_and_td()
	if step == "alg" or step == "all":
		algorithm()
	if step == "md5" or step == "all":
		md5_test()
	if step == "del_d" or step == "all":
		del_duplicate()

