#!/usr/bin/python
#coding=utf-8
import re
#import BeautifulSoup
#import chardet

CHAR_ENTITIES = {'nbsp':' ', '160':' ', 'lt':'<', '60':'<', 'gt':'>',\
			'62':'>', 'amp':'&', '38':'&', 'quot':'"', '34':'"'}

def replace_char_entity(htmlstr):
	"""
		Use the normal chars replace the HTML special character.
	"""
	re_char_entity = re.compile(r'&#?(?P<name>\w+);')
	se_str = re_char_entity.search(htmlstr)
	while se_str:
		key = se_str.group('name')
		try:
			htmlstr = re_char_entity.sub(CHAR_ENTITIES[key], htmlstr, 1)
			se_str = re_char_entity.search(htmlstr)
		except KeyError:
			htmlstr = re_char_entity.sub('', htmlstr, 1)
			se_str = re_char_entity.search(htmlstr)
	return htmlstr

def filter_tags(htmlstr):
	"""
		Remove Html struct labels. Get the content only.
	"""
	dlist = []
	h_str = htmlstr
	re_br = re.compile('<br\\s*?/?>') #deal wrap
	h_str = re_br.sub('\n', h_str) #br to \n

	dlist.append(re.compile('<![doctype|DOCTYPE][^>]*>', re.I))
	dlist.append(re.compile('//<!\\[CDATA\\[[^>]*//\\]\\]>', re.I))
	dlist.append(re.compile('<\\s*script[^>]*>[^<]*<\\s*/\\s*script\\s*>',\
			re.I))
	dlist.append(re.compile('<\\s*style[^>]*>[^<]*<\\s*/\\s*style\\s*>',\
			re.I))
	dlist.append(re.compile('</?\\w+[^>]*>'))
	dlist.append(re.compile('<!--[^>]*-->'))

	for del_re in dlist:
		h_str = del_re.sub('', h_str)

	return replace_char_entity(h_str)

def html_charset(html):
	""" Get html charset."""
	badcode = {"gbk2312":"gb2312"}
	pos = 0
	pos = html.lower().index("charset=")
	if pos == -1:
		return False

	cutstr = html[pos:pos+20].lower().replace("charset=", "")
	offset = cutstr.rfind('"')
	code = cutstr[:offset].replace("\"", "")
	if code.lower() in badcode:
		code = badcode[code.lower()]
	return code

def html2utf8(html, def_code=None):
	""" Encode html to utf8."""
	code = html_charset(html)
	if code:
		html = html.decode(code, "ignore").encode('utf-8')
		return html
	elif def_code:
		html = html.decode(def_code, "ignore").encode('utf-8')
		return html
	return False
