#!/usr/bin/python
#coding=utf-8
"""
	Unit test for sql.py.
"""
import os
import sys
import time
import commands
from pylib import sql

TEST_MYSQL = {"host":"106.186.121.217", "user":"test", "pw":"123", "port":3306}

def sql_test():
	print "==== sql class test."
	print "==== step 1, connect"
	agent = sql.Sql(TEST_MYSQL, "test", assoc=True, sql_type=sql.TYPE_MYSQL)
	agent.check_connect()

	print "==== step 2, insert"
	agent.insert("test", {"md5":"123", "html":"456", "state":1})
	insert_list = [{"md5":"987", "html":"234", "state":1},\
			{"md5":"789", "html":"101", "state":1}]
	agent.insert("test", insert_list)

	print "==== step 3, select"
	rows = agent.select("test", ["md5"], "where id>0")
	for row in rows:
		if not row["md5"] in ["123", "789", "987"]:
			print rows
			break
	rows = agent.select("test", ["md5"], {"state":1})
	for row in rows:
		if not row["md5"] in ["123", "789", "987"]:
			print rows
			break

	print "==== step 4, update"
	agent.update("test", {"state":0}, {"md5":"123"})
	agent.update("test", {"state":0}, "where md5='789'")
	rows = agent.select("test", ["md5"], {"state":0})
	if rows != ({'md5': '123'}, {'md5': '789'}):
		print rows

	print "==== step 5, exist"
	if not agent.exist("test", {"md5":"123"}) and agent.exist("test", {"md5":"x"}):
		print "exist error."
	exist_list = ["456", "101", "sdf"]
	ret_list = agent.exist("test", exist_list, "html")
	if ret_list != {'101': 1, '456': 1}:
		print ret_list

	print "==== step 6, execute"
	ret = agent.execute("delete from test")
	rows = agent.select("test", ["*"], "where id>0")
	if not ret or rows:
		print "execute failed."







if __name__ == "__main__":
	step = "all"
	if len(sys.argv) > 1:
		step = sys.argv[1]
	if step == "sql" or step == "all":
		sql_test()

