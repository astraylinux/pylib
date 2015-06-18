#!/usr/bin/python
#coding=utf8
import re
import json
from lxml import etree

class PathBasic(object):
	"""
		Pick basic class, some fixed functions and attributes.
		Use the config to pick info from confusion html.
	"""
	def __init__(self, url, html, code="gbk"):
		self._url = url
		self._html = unicode(html.decode(code))
		row = url.split("/")
		self._domain = row[2]
		self._url_domain = row[0] + "//" + row[2]
		if url[-1] == "/":
			self._path = url
		else:
			self._path = url.replace(url.split("/")[-1], "")

	def _merge_url(self, url_sub):
		""" If the url is relative path, convert to entire url."""
		if not url_sub:
			return
		if "http://" in url_sub:
			return url_sub
		elif url_sub[0] == "/":
			return str(self._url_domain + url_sub)
		else:
			return str(self._path + url_sub)

	def _ex_func(self, rstr, func):
		"""
			Some extend function deal the result string that is appointed
			in config, they are split, replace, re(refular expression), re.sub.
			Is used to reprocess result string from one field.
		"""
		method = func["method"]
		argv = func["argv"]
		result = ""
		if method == "split":
			if not argv[0] in rstr:
				return rstr
			row = rstr.split(argv[0])
			if ", " in argv[1]:
				for index in argv[1].split(", "):
					result += row[int(index)]
			else:
				result = row[int(argv[1])]
		elif method == "replace":
			result = rstr.replace(argv[0], argv[1])
		elif method == "re":
			match = re.search(argv[0], rstr)
			result = rstr
			if match:
				result = match.group()
		elif method == "re.sub":
			ret = re.sub(argv[0], argv[1], rstr)
			result = rstr
			if ret:
				result = ret
		else:
			result = rstr
		return result

	def _path_pre(self, val):
		""" Do something before execute xpath or else."""
		sentence = val["key"]
		return sentence

	def _path_after(self, rstr, val):
		""" Do someting after xpath, it's _ex_func and _merge_url now."""
		if "remake" in val:
			for func in val["remake"]:
				rstr = self._ex_func(rstr, func)
		path = val["key"]
		if (path[-5:] == "@href" or path[-4:] == "@src") and not "not_abs_url" in val:
			rstr = self._merge_url(rstr)
		return rstr

	def _deal_value_data(self, ret):
		""" Deal the data that will be a last value."""
		return ""

	def _path2array(self, tree, config):
		"""
			Main process of pick.
		"""
		result = {}
		for key, val in config.items():
			if key == "delete":
				continue
			#pick result is string.
			if not "type" in val:
				sentence = self._path_pre(val)
				ret = self._picker(tree, sentence)
				if not ret:
					result[key] = None
					continue

				ret = self._deal_value_data(ret)
				ret = self._path_after(ret, val)
				result[key] = ret
			#pick result is list.
			elif val["type"] == "list":
				rlist = []
				blocks = self._picker(tree, val["block"])
				for block in blocks:
					ret = self._path2array(block, val["data"])
					if ret:
						rlist.append(ret)
				result[key] = rlist
			#pick result is dict.
			elif val["type"] == "dict":
				ret = self._path2array(tree, val["data"])
				result[key] = ret
		return result

	def _picker(self, tree, sentence):
		""" Real pick process. Must be rewrited."""
		return

	def _pick(self, config):
		""" According to the pick type, input the config data. Must be rewrited."""
		return

	def pick(self, config):
		""" Public api. Don't rewrite this."""
		ret = self._pick(config)
		if not ret:
			return ret
		if len(ret) > 1:
			return ret
		for key in ret:
			if isinstance(ret[key], list):
				return ret[key]
			return ret

######################################################  use xpath
class XPath(PathBasic):
	""" Pick class that use etree.xpath."""
	def _picker(self, tree, sentence):
		return tree.xpath(sentence)

	def _deal_value_data(self, ret):
		if etree.iselement(ret[0]):
			ret[0] = etree.tostring(ret[0], encoding="utf8")
		return str(ret[0])

	def _pick(self, config):
		parser = etree.HTMLParser()
		tree = etree.fromstring(self._html, parser)
		if "delete" in config:
			for path in config["delete"]:
				if tree.xpath(path):
					tree.xpath(path)[0].clear()
		return self._path2array(tree, config)

###################################################### json data
class XJson(PathBasic):
	""" Pick class to pick data from json, for api unification."""
	def _picker(self, tree, sentence):
		keys = sentence.split("/")
		tmp = tree
		for key in keys:
			if len(key) == 0:
				continue
			if not key in tmp:
				if key.isdigit() and isinstance(tmp, list) and len(tmp) > int(key):
					key = int(key)
				else:
					return False
			tmp = tmp[key]
		if isinstance(tmp, unicode) or isinstance(tmp, str):
			return [tmp]
		return tmp

	def _deal_value_data(self, ret):
		if isinstance(ret, list):
			return ret[0]
		return ret

	def _pick(self, config):
		tree = json.loads(self._html)
		return self._path2array(tree, config)
