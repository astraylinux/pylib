#!/usr/bin/python
#coding=utf-8
"""

"""
import json
import datetime
import hashlib
import MySQLdb
import MySQLdb.cursors
#import pymssql

TYPE_MYSQL = 0
TYPE_MSSQL = 1

def has_injection(args):
	""" Sql injection prevention. """
	sql_key = [" and ", "execute ", "update ", "count ", "chr ",\
			"mid ", "master ", "truncate ", " char", "", "declare ",\
			"select ", "create ", "delete ", "insert ", "'",\
			'"', " or ", "="]
	for i in range(0, len(args)):
		for key in sql_key:
			if key in args[i]:
				return True
	return False

def trans2str(field):
	""" Convert a sql type to string."""
	output = field
	if isinstance(field, datetime.date):
		try:
			output = field.strftime("%Y-%m-%d %H:%M:%S")
		except:
			output = "2014-01-01 00:00:00"
	elif isinstance(field, long):
		output = str(field)
	elif isinstance(field, int):
		output = str(field)
	elif isinstance(field, unicode):
		output = field.encode('utf8')
	elif isinstance(field, float):
		output = str(int(field))
	return output

def trans_key_dict(rows, key, columns=None):
	"""
		Transformat rows(dict or list) to a dict, that use the
		row[key]'s value as a dict key, and row as the value.
		The row[key]'s value must be unique.
	"""
	result = {}
	if isinstance(rows[0], dict):
		for row in rows:
			result[row[key]] = row
	elif isinstance(rows[0], list) and columns:
		index = 0
		for i in range(0, len(columns)):
			if key == columns[i]:
				index = i
				break
		for row in rows:
			result[row[index]] = row

def get_where(data):
	"""
		Convert dict where data to sql string.
		data is string, return data directly.
		data is dict, value not list, use 'field=value' sql syntax.
		data is dict, value is list, use 'in()' sql syntax, (only one key).
	"""
	if type(data) in [str, unicode]:
		return " " + data

	if isinstance(data, dict):
		wsql = " where "
		items = data.items()
		for (field, values) in items:
			value_type = type(values)
			if value_type in [int, long, float]:
				wsql = wsql + "%s=%s and "%(field, str(values))
			elif value_type in [str, unicode]:
				wsql = wsql + "%s='%s' and "%(field, values)
			elif value_type == list:
				wsql = wsql + field + " in ("
				for value in values:
					if type(value) in [int, long]:
						wsql += "%s,"%value
					else:
						wsql += "'%s',"%value
				wsql = wsql[:-1] + ")"
			else:
				wsql = wsql + "%s='%s' and "%(field, trans2str(values))
		if wsql.endswith(" and "):
			wsql = wsql[:-5]
		return wsql

class Sql(object):
	"""
		Simport package of sql, Support mysql and sqlserver.
		Mysql depend on MySQLdb, Sqlserver depend on pymssql.

	"""
	def __init__(self, server, db_name, assoc=False, sql_type=TYPE_MYSQL,\
			charset="utf8"):
		"""
			server: a dict with info of server.
				{"host":"localhost","user":"test","pw":"123", "port":3306}
			db_name: name of database.
			use_dict: select return dict when it's true, else return list.
			sql_type: choose mysql or mssql, mysql default.
			charset: default is utf8.
		"""
		self._server = server
		self._host = server["host"]
		self._user = server["user"]
		self._pw = server["pw"]
		self._port = 3306
		self._db = db_name
		self._assoc = assoc
		self._type = sql_type
		self._cursor = None
		self._conn = None
		self._charset = charset

		if "port" in server:
			self._port = server["port"]

		if sql_type == TYPE_MYSQL:
			cursor_class = MySQLdb.cursors.Cursor
			if self._assoc:
				cursor_class = MySQLdb.cursors.DictCursor
			self._conn = MySQLdb.connect(self._host, self._user,\
						self._pw, db_name, self._port, \
						cursorclass=cursor_class)
			self._cursor = self._conn.cursor()
			self._cursor.execute("set names " + self._charset)
		elif sql_type == TYPE_MSSQL:
			self._conn = pymssql.connect(self._host, self._user, \
					self._db, self._pw, charset=self._charset)
			self._cursor = self._conn.cursor()


	def check_connect(self):
		""" Check is cursor connecting, if not, reconnect."""
		try:
			self._conn.ping()
		except Exception:
			self.__init__(self._server, self._db, self._assoc, \
					self._type, self._charset)

	def commit(self):
		""" if database is Innodb, should execute commit after write."""
		self._conn.commit()

	def execute(self, sql, value_list=None):
		""" Execute normal SQL sentence."""
		if value_list:
			return self._cursor.execute(sql, value_list)
		return self._cursor.execute(sql)

	def _insert(self, table, data, ignore_key="id", output=False):
		"""
			Sql insert. data is a dict with field and value.
			ignore_key: for duplicate key to update. id is ok.
			output: if output true will print result sql.
		"""
		rsql = "insert into " + table + "("
		value = ") value("
		rlist = []
		for key in data:
			rsql = rsql + key + ','
			value = value + "%s,"
			rlist.append(trans2str(data[key]))
		rsql = rsql[0:-1]
		value = value[0:-1]
		rsql = rsql + value + ") on duplicate key update %s=%s"%(\
				ignore_key, ignore_key)
		if output:
			print rsql%tuple(rlist)
		return self._cursor.execute(rsql, rlist)

	def _insert_list(self, table, datas, ignore_key="id", output=False):
		"""
			Insert sql, datas is a list of dictionaries.
			ignore_key: for duplicate key to update. id is ok.
			output: if output true will print result sql.
		"""
		rsql = "insert into " + table + "("
		values = ") value("
		rlist = []
		data1 = datas[0]
		for key in data1:
			rsql = rsql + key + ','
			values = values + "%s,"
		for data in datas:
			rdata = []
			for (key, value) in data.items():
				rdata.append(trans2str(value))
			rlist.append(rdata)
		rsql = rsql[0:-1]
		values = values[0:-1]
		rsql = rsql + values + ") on duplicate key update %s=%s"%(\
				ignore_key, ignore_key)
		if output:
			print rsql
		return self._cursor.executemany(rsql, rlist)

	def insert(self, table, data, ignore_key="id", output=False):
		""" Public api, data could be list or dict."""
		if isinstance(data, list):
			return self._insert_list(table, data, ignore_key, output)
		else:
			return self._insert(table, data, ignore_key, output)

	def update(self, table, data, where_data, output=False):
		"""
			Sql update. will print sql while output is true.
			data: a dict with field name as key, and value.
			where_data: could be dict for field limit value
						or just sql string.
		"""
		rsql = "update " + table + " set "
		rlist = []
		for key in data:
			rsql = rsql + key + "=%s,"
			rlist.append(trans2str(data[key]))
		rsql = rsql[0:-1]
		rsql = rsql + get_where(where_data)
		if output:
			print rsql%tuple(rlist)
		return self._cursor.execute(rsql, rlist)

	def _select(self, table, keylist, where_data, \
			one=False, output=False):
		"""
			Private Sql selet. will print sql while output is true.
			keylist: a list with field name, just "*" is all field.
			where_data: could be dict for field limit value
						or list to use 'in()' sql sytax,
						or just sql string.
			one: if true, use fetchone, only get one result.
		"""
		rsql = "select "
		for key in keylist:
			rsql = rsql + key + ","
		rsql = rsql[0:-1]
		rsql = rsql + " from " + table + get_where(where_data)
		if output:
			print rsql
		self._cursor.execute(rsql)
		if one:
			return self._cursor.fetchone()
		else:
			return self._cursor.fetchall()

	def select(self, table, keylist, where_data, one=False, output=False):
		"""Public api of sql select. use the _select."""
		return self._select(table, keylist, where_data, one, output)

	def _exist(self, table, condition, key=None):
		"""
			Check if database row with the condition existed.
			If condition is a dict, key could be None.
			If condition is a string, must specific key field.
		"""
		if isinstance(condition, dict):
			rsql = "select " + condition.keys()[0] + " "
		else:
			rsql = "select " + key + " "
		rwhere = get_where(condition)
		rsql = rsql + " from " + table + rwhere
		self._cursor.execute(rsql)
		if self._cursor.fetchone():
			return True
		return False

	def _exist_list(self, table, condition, key=None):
		"""
			Checl if database rows in the condition list.
			If key is None, Condition must be a list with dict.
				Condition is a list include many dict.
				Each dict must and the only one and same key.
			If key is'n None, condition is a list with the field values.
			Return a dict that include all the existed values.
		"""
		if len(condition) == 0:
			return []
		if not key:
			field = condition[0].keys()[0]
		else:
			field = key
			condition = {field: condition}

		rows = self._select(table, [field], condition)
		ret = {}
		if not rows:
			return ret
		if isinstance(rows[0], dict):
			for row in rows:
				ret[row[field]] = 1
		else:
			for row in rows:
				ret[row[0]] = 1
		return ret

	def exist(self, table, condition, key=None):
		""" Public api of exsit, use _exist or _exist_list."""
		if isinstance(condition, list):
			return self._exist_list(table, condition, key)
		else:
			return self._exist(table, condition, key)



#============================================ just test
def data2redis(redis, queue, table, operate_type, data, key, division=1):
	"""
		Push the sql command data to redis.
		Let another program use the data.
		redis: target redis server's connect agent.
		queue: target redis queue's name.
		table: the target of sql operating's table.
		operate_type: insert, update or delete.
		data: the sql operating's target data.
		key: the unique field. Data identity field.
		division: sql table division number.
	"""
	result = {}
	if division == 1:
		result["table"] = table
	else:
		md5 = None
		if key == "md5":
			md5 = data[key]
		else:
			md5 = hashlib.md5(data[key])
		index = str(int(str(md5)[-16:].upper(), 16)%division)
		result["table"] = table + index

	result["type"] = operate_type
	result["key"] = key
	result["data"] = data
	jstr = json.dumps(result)
	return redis.lpush(queue, jstr)
