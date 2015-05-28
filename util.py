#!/usr/bin/python
#coding=utf-8
import sys,os
import redis
import logging
import time
import socket
import hashlib
import datetime
import random
import _langconv
import re
from decimal import Decimal
#import subprocess

py_map = {}
#================================= util ==================================
#---- redis
def GetRedisClient(server):
	return redis.Redis(host=server["host"],port=server["port"],db=server["db"])

#---- logging config
def GetLogger(logfile,flag,name,formatstr=None,level=logging.INFO):
    logger = logging.getLogger(name)
    ch = logging.handlers.RotatingFileHandler(logfile)
    if not formatstr:
        formatstr = "["+flag+"][%(asctime)s][%(filename)s][%(lineno)d][%(levelname)s]::%(message)s"
    formatter = logging.Formatter(formatstr)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(level)
    return logger

def LogConfig(logfile,level=logging.INFO,fmt=None):
    if not fmt:
        fmt = "[%(asctime)s][%(filename)s][%(lineno)d][%(levelname)s]::%(message)s"
    logging.basicConfig(filename=logfile,level=level,format=fmt)

#---- date
def GetNowDatetime():
    return time.strftime('%Y-%m-%d-%H:%M:%S',time.localtime(time.time()))

def GetDate(offset=-1):
	today     = datetime.date.today()
	offset_d  = datetime.timedelta(days=offset)
	the_date  = today + offset_d 
	return str(the_date)

def GetTime():
	return Decimal(datetime.datetime.utcnow().microsecond)/1000000 + Decimal(int(time.time()))

def Date2second(the_date):
    return int(time.mktime(time.strptime(str(the_date)[:19], "%Y-%m-%d %H:%M:%S")))

def Second2date(second):
    timeArray = time.localtime(second)
    return time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
	
#---- socket
def Getip():
    ip = socket.gethostbyname(socket.gethostname())
    return ip
   
# 
def GetApkid(sku):
    md5 = hashlib.md5(sku).hexdigest()
    high = hex2dec(md5[1:16])
    low = hex2dec(md5[17:32])
    apkid = int(high) + int(low)
    return apkid
    
#---- md5
def GetMd5(string):
    return hashlib.md5(string).hexdigest()
   
#---- mp3 info
def GetMp3Info(mp3,flag=""):
	tmpfile = "/tmp/mp3info.tmp" + flag
	os.system("cutmp3 -I " + mp3 + " >" + tmpfile)
	tmp = open(tmpfile)
	info = tmp.read()
	tmp.close()
	return info

def GetMp3Length(mp3):
	info = GetMp3Info(mp3)
	s_index = info.index("second(s)")
	m_index = info.index("minute(s)")
	second = int(float(info[s_index - 8:s_index-1].split(" ")[-1]))
	minute = int(info[m_index-5:m_index-1].split(" ")[-1])
	length = minute * 60 + second
	return length

#---- 
def GetMd5Path(md5):
	return md5[-1] + '/' + md5[29:-1] + '/'	

#========================== 文字转换 =================================
#中文转拼音
def trans2py(cn_str,entire=True):
	#如果py_map是空的，则初始化
	if not py_map:
		path = os.path.dirname(__file__)
		fp	= open(path + "/data/pinyin-utf8.db","r+")
		lines = fp.readlines()
		fp.close()
		for line in lines:
			sp = line.replace("\n","").split(",")
			py_map[sp[0]] = sp[1][:-1]

	#汉字转拼音
	i = 0
	rstr = ""
	try:
		cn_str = cn_str.encode("utf8")
	except Exception,e:
		#print e
		return ""

	cn_str = unicode(cn_str)
	namecn	= ""
	sp = cn_str.split(" ")
	for s in sp:
		if namecn != "":
			namecn += " "
		matches = re.findall(u"[\u4e00-\u9fa5]",s)
		for match in matches:
			namecn += str(match)
	
	if not namecn:
		return ""
	while i < len(namecn):
		zi = namecn[i:i+3] 
		if zi in py_map:
			if not entire:
				rstr += py_map[zi][0]
			else:
				rstr += py_map[zi]
		if i+3 < len(namecn) and namecn[i+3] == " ":
			rstr += " "
			i += 1
		i = i+3
	return rstr

#简体字转繁体字
def conver_sp2td(cn_str):
	cn_str = _langconv.Converter('zh-hant').convert(cn_str.decode('utf-8'))
	return cn_str.encode('utf-8')

#繁体转简体
def conver_td2sp(cn_str):
	cn_str = _langconv.Converter('zh-hans').convert(cn_str.decode('utf-8'))
	return cn_str.encode('utf-8')

#========================== 数据结构 ==================================
def GetRandList(alist,num,propertys=[]):
	#从现有队列生成随机队列,可以加权
	default = 1
	section = 0
	count   = 0
	ranges	= []
	rlist	= []

	if propertys:
		for key in propertys:
			default = default + propertys[key]
		default = int(default/len(propertys))

	#生成权重范围队列
	for key in alist: 
		if key in propertys:
			section = section + propertys[key]
		else:
			section = section + default
		#print key,section
		ranges.append(section)
	
	while count < num:
		index = 0
		ri = random.randint(0,section)
		while ri > ranges[index]:
			index = index + 1
		item = alist[index]
		if item in rlist:
			continue
		rlist.append(item)
		count = count + 1
		#print ri,item
	return rlist

#---- Algorithm 
def GetSortList(key_map,desc=False):
	items = key_map.items()
   	backitems = [[v[1],v[0]] for v in items]
   	backitems.sort()
   	key_list = []
   	if desc:
   	        return [backitems[i][1] for i in range(len(backitems)-1,-1,-1)]
   	else:
   	        return [backitems[i][1] for i in range(0,len(backitems))]

def SortList4MapItem(List,key,desc=False):
	backitems = [[v[key],v] for v in List]
	backitems.sort()
	if desc:
   	        return [backitems[i][1] for i in range(len(backitems)-1,-1,-1)]
   	else:
   	        return [backitems[i][1] for i in range(0,len(backitems))]

def List2Str(items,sep):
	rstr = ""
	for item in items:
		rstr = rstr + str(item) + sep
	return rstr[:-1]

def GetRankMap(map,num,desc=False):
	rlist = GetSortList(map,desc)
	n_map = {}
	for key in rlist[:num]:
		n_map[key] = map[key]
	return n_map

def List2dict(rows,keys):
    result = []
    length = len(keys)
    for row in rows:
        data = {}
        for i in range(0,length):
            data[keys[i]] = row[i]
        result.append(data)
    return result

#==================================== FILE ==========================================
def GetLines(file_name):
	#读取文件行
	fp 	= open(file_name,'r+')
	lines 	= fp.readlines()
	fp.close()
	for i in range(0,len(lines)):
		lines[i] = lines[i].replace('\n','')
	return lines

def GetFileMd5(strFile):  
    fi = None;  
    bRet = False;  
    strMd5 = "";  
    try:  
        fi = open(strFile, "rb");  
        md5 = hashlib.md5();  
        strRead = "";  
        while True:  
            strRead = fi.read(8096);  
            if not strRead:  
                break;  
            md5.update(strRead);  
        #read file finish  
        bRet = True;  
        strMd5 = md5.hexdigest();  
    except:  
        bRet = False;  
    finally:   
        if fi:  
            fi.close()  
    return strMd5 

#对list去重，如果list的项是dict要给出去重用的key
def DuplicateList(in_list,key=None):
	result = []
	tmp = {}
	for item in in_list:
		data = item
		if isinstance(item,dict):
			data = item[key]
		if not data in tmp:
			result.append(item)
			tmp[data] = 1
	return result

#============================================================================= 字符串
def Trim(string):
	start = 0
	end = 0
	for i in string:
		if i in " \t\n\r":
			start += 1
		else:
			break
	for i in string[::-1]:
		if i in " \t\n\r":
			end -= 1
		else:
			break
	if end == 0:
		return string[start:]
	else:
		return string[start:end]

#============================================================================== 进制转换
# base = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, A, B, C, D, E, F]
base = [str(x) for x in range(10)] + [ chr(x) for x in range(ord('A'),ord('A')+6)]

# bin2dec
def Bin2dec(string_num):
    return str(int(string_num, 2))

# hex2dec
def Hex2dec(string_num):
    return str(int(string_num.upper(), 16))

# dec2bin
def Dec2bin(string_num):
    num = int(string_num)
    mid = []
    while True:
        if num == 0: break
        num,rem = divmod(num, 2)
        mid.append(base[rem])
    return ''.join([str(x) for x in mid[::-1]])

# dec2hex
def Dec2hex(string_num):
    num = int(string_num)
    mid = []
    while True:
        if num == 0: break
        num,rem = divmod(num, 16)
        mid.append(base[rem])
    return ''.join([str(x) for x in mid[::-1]])

# hex2tobin
def Hex2bin(string_num):
    return dec2bin(hex2dec(string_num.upper()))

# bin2hex
def Bin2hex(string_num):
    return dec2hex(bin2dec(string_num))

def GetUrlmd5i(strmd5):
    return hex2dec(str(strmd5)[0:13])

#============================================================================== shell
#def getPIPE(cmd): #cmd like ["echo","output string"]
#	#p = subprocess.Popen(["/bin/bash"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True)
#	p = subprocess.Popen(["cat","/proc/cpuinfo"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True)
#	result = ""
#	while True:
#		pstr = p.stdout.readline()
#		print pstr
#		if pstr:
#			result = result + pstr + "\n"
#			continue
#		break
#	return result







